"""Step 4: turn a markdown file into a graph.

    docker compose up -d

    # See how the file will be split. No LLM calls, no writes, free.
    python ingest_markdown.py notes.md --dry-run

    # Ingest one section first and inspect what got extracted.
    python ingest_markdown.py notes.md --group-id notes --limit 1

    # Then the rest.
    python ingest_markdown.py notes.md --group-id notes

One episode per markdown section, because Graphiti runs a full
extract-entities -> extract-edges -> dedupe cycle per episode. The whole file
as one episode makes the LLM find every entity in a single pass and it returns
a shallow set; one line per episode is too small to contain a relationship.
A section is the unit that holds a complete thought.

On FalkorDB a group_id is a *separate graph*, not a property filter, so
--group-id keeps this document out of your other data. Search it with
`group_ids=[...]` (the group dropdown in app.py), not a bare search.
"""

import argparse
import asyncio
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from add_episodes import make_graphiti

from groq import APIStatusError  # noqa: E402

from graphiti_core.llm_client.errors import RateLimitError  # noqa: E402
from graphiti_core.nodes import EpisodeType  # noqa: E402
from graphiti_core.utils.content_chunking import (  # noqa: E402
    chunk_text_content,
    estimate_tokens,
)

# Graphiti wraps each episode body in a system prompt, few-shot examples and
# the list of already-extracted entities, so the request is much larger than
# the body. Measured: a 1606-token section produced an 8067-token request.
# The overhead also grows as the graph fills up, because the dedupe prompts
# carry more existing entities, so treat this as a floor rather than a rule.
PROMPT_OVERHEAD_TOKENS = 6400

# Left to itself the extractor returns relationships between named entities
# and drops attribute data. Measured on this corpus: "| Established | 2012 |"
# produced no fact at all, and of six focus groups on one line only the four
# proper nouns (Bodo, Rabha, Garo, Adivasi) survived -- "rural women" and
# "tea-garden workers" were dropped for being common nouns.
#
# The organization-type line also matters for this corpus: the source warns
# that the KABIL NGO is not Khanij Bidesh India Limited, a mining PSU of the
# same acronym, and without typing they extract as one conflated entity.
#
# The closing table paragraph is doing separate work: a table row has no
# subject of its own, so without it the row is not a statement about anything.
EXTRACTION_INSTRUCTIONS = """Extract all important factual information from \
the source.

Capture:
- organizations and their organization type
- NGOs, PSUs, government bodies and funders
- people and their roles
- locations
- projects and programs
- funding relationships
- beneficiary and demographic groups, including generic categories
- dates and years
- registration information
- compliance statuses such as 12A, 80G and FCRA
- beneficiary counts
- funding/grant amounts
- registration numbers

Do not omit information merely because a value is a date, number, amount, \
yes/no value, or generic demographic category.

Preserve relationships between organizations, funders, projects, locations \
and beneficiary groups.

A markdown table row written as | Field | Value | is a statement about the \
subject of the section it appears in, not about the field name. Attribute it \
to that subject: in a section about an organisation, | Established | 2012 | \
means that organisation was established in 2012."""

# Opening fence (with optional language) through the closing fence.
CODE_FENCE_RE = re.compile(r"^```[^\n]*\n.*?^```[ \t]*$", re.MULTILINE | re.DOTALL)


def split_by_heading(text: str, level: int) -> list[str]:
    """Split on markdown headings of exactly `level`, keeping each heading
    attached to the body beneath it. Returns [] if there are no such headings.

    Any preamble before the first heading is returned as its own leading
    section, so an H1 title and intro paragraph are not silently dropped.
    """
    pattern = re.compile(rf"^#{{{level}}} [^\n]*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    if not matches:
        return []

    sections = []
    preamble = text[: matches[0].start()].strip()
    if preamble:
        sections.append(preamble)

    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section = text[match.start() : end].strip()
        if section:
            sections.append(section)
    return sections


def heading_of(section: str) -> str | None:
    """The section's heading text, for naming the episode.

    None when the piece has no heading -- a token-split chunk, or a file with
    no headings at all. The caller supplies a name in that case; using the
    first line of prose would make the episode name the whole paragraph.
    """
    first = section.lstrip().split("\n", 1)[0]
    if not first.startswith("#"):
        return None
    return first.lstrip("#").strip() or None


def split_section(section: str, max_tokens: int) -> list[str]:
    """Cut an oversized section down: H3 subsections first, then Graphiti's
    token chunker as a last resort.

    Heading splits are preferred because they fall on topic boundaries;
    chunk_text_content() splits on token count and will cut mid-argument.
    """
    if estimate_tokens(section) <= max_tokens:
        return [section]

    pieces = []
    for sub in split_by_heading(section, 3) or [section]:
        if estimate_tokens(sub) <= max_tokens:
            pieces.append(sub)
        else:
            pieces.extend(chunk_text_content(sub, chunk_size_tokens=max_tokens))
    return pieces


def build_episodes(
    text: str, max_tokens: int, strip_code: bool, level: int, fallback: str = "section"
) -> list[tuple[str, str]]:
    """Plan the ingest: a list of (episode name, episode body).

    Each body is prefixed with the document title so a section that says "it"
    or "the model" still has a subject the extractor can resolve.
    """
    if strip_code:
        text = CODE_FENCE_RE.sub("", text)

    title_match = re.search(r"^# ([^\n]+)$", text, re.MULTILINE)
    doc_title = title_match.group(1).strip() if title_match else ""

    sections = split_by_heading(text, level)
    if not sections:
        # No headings at that level -- fall back to the token chunker.
        sections = chunk_text_content(text, chunk_size_tokens=max_tokens)

    episodes = []
    for section in sections:
        for piece in split_section(section, max_tokens):
            name = heading_of(piece) or f"{fallback} part {len(episodes) + 1}"
            body = f"Document: {doc_title}\n\n{piece}" if doc_title else piece
            episodes.append((name[:120], body))

    # Disambiguate repeated headings so episode names stay unique.
    seen: dict[str, int] = {}
    out = []
    for name, body in episodes:
        seen[name] = seen.get(name, 0) + 1
        out.append((f"{name} ({seen[name]})" if seen[name] > 1 else name, body))
    return out


async def already_ingested(graphiti) -> set[str]:
    """Names of episodes already written to the target graph."""
    try:
        result = await graphiti.driver.execute_query(
            "MATCH (e:Episodic) RETURN e.name AS name"
        )
    except Exception:
        return set()
    rows = result[0] if isinstance(result, tuple) else result
    names = set()
    for row in rows or []:
        name = row.get("name") if isinstance(row, dict) else row[0]
        if name:
            names.add(name)
    return names


class TooLargeForTPM(RuntimeError):
    """One episode exceeded the model's tokens-per-minute ceiling."""


class DailyQuotaExhausted(RuntimeError):
    """The per-day token budget is gone. Nothing helps until it resets."""


def _quota_detail(exc: BaseException, depth: int = 6) -> str:
    """Every message on an exception's chain, joined.

    Wrappers routinely drop the provider's text: graphiti raises its own
    RateLimitError with no arguments, so the sentence naming TPD or TPM is
    only reachable through __cause__.
    """
    parts, seen, cur = [], set(), exc
    while cur is not None and len(parts) < depth and id(cur) not in seen:
        seen.add(id(cur))
        parts.append(str(cur))
        cur = cur.__cause__ or cur.__context__
    return " | ".join(parts)


async def add_with_retry(graphiti, retries: int = 7, **kwargs):
    """add_episode, retrying on Groq's rate limit with increasing backoff.

    Each episode is several LLM calls, so a long document will hit the
    tokens-per-minute ceiling well before the requests-per-minute one.
    """
    delay = 20
    for attempt in range(retries):
        try:
            return await graphiti.add_episode(**kwargs)
        except RateLimitError as exc:
            # A per-minute limit refills in under a minute, so backing off
            # works. A per-day limit does not refill for hours: backing off
            # burns 21 minutes per episode and skips it anyway.
            #
            # Groq names which limit it hit, but graphiti's GroqClient does
            # `raise RateLimitError from e` with no arguments, so str(exc) is
            # always the generic "Rate limit exceeded. Please try again
            # later." The real text only survives on the exception chain.
            detail = _quota_detail(exc)
            if "tokens per day" in detail or "(TPD)" in detail:
                raise DailyQuotaExhausted(detail) from exc
            if attempt == retries - 1:
                raise
            print(f"    rate limited, waiting {delay}s...", flush=True)
            await asyncio.sleep(delay)
            delay *= 2
        except APIStatusError as exc:
            # 413: this single request is bigger than the whole per-minute
            # budget. Retrying sends the identical payload and fails the same
            # way, so surface it as a sizing problem instead.
            if exc.status_code != 413:
                raise
            raise TooLargeForTPM(str(exc)) from exc


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("path", type=Path, help="markdown file to ingest")
    parser.add_argument(
        "--group-id",
        help="isolate this document in its own FalkorDB graph (recommended)",
    )
    parser.add_argument(
        "--level", type=int, default=2, help="heading level to split on (default 2)"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=1200,
        help=(
            "split sections larger than this (default 1200). Sized to fit "
            "under an 8000 TPM limit given ~%d tokens of prompt overhead. Do "
            "not lower it to 'be safe': the overhead is per call, so smaller "
            "episodes mean more calls and a bigger total bill"
            % PROMPT_OVERHEAD_TOKENS
        ),
    )
    parser.add_argument(
        "--tpm",
        type=int,
        default=8000,
        help=(
            "your model's tokens-per-minute limit, used to flag episodes that "
            "will fail with HTTP 413 (default 8000, the Groq on-demand tier)"
        ),
    )
    parser.add_argument(
        "--pace",
        type=float,
        default=0.0,
        help="seconds to wait between episodes, to stay under the TPM budget",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help=(
            "ingest at most N episodes this run. Counted after "
            "--skip-existing, so it means N more, leaving quota for other work"
        ),
    )
    parser.add_argument(
        "--keep-code", action="store_true", help="keep fenced code blocks"
    )
    parser.add_argument(
        "--extraction-instructions",
        help=(
            "override the built-in instructions telling the extractor to "
            "capture dates, numbers, amounts, counts and demographic "
            "categories as facts"
        ),
    )
    parser.add_argument(
        "--no-extraction-instructions",
        action="store_true",
        help="let the extractor decide everything itself (the old behaviour)",
    )
    parser.add_argument(
        "--no-previous-context",
        action="store_true",
        help=(
            "stop attaching earlier episode bodies to each prompt. Graphiti "
            "attaches up to 10 (RELEVANT_SCHEMA_LIMIT) to both the extract "
            "and dedupe prompts, which grows the request until it exceeds an "
            "8000 TPM ceiling no matter how small the episode is. Costs some "
            "cross-section context, e.g. resolving 'it' to an earlier subject"
        ),
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help=(
            "skip episodes whose name is already in the target graph, so an "
            "interrupted run can be resumed without re-paying for it"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show the split and exit: no LLM calls, no writes",
    )
    args = parser.parse_args()

    if not args.path.is_file():
        print(f"no such file: {args.path}", file=sys.stderr)
        return 1

    text = args.path.read_text(encoding="utf-8")
    episodes = build_episodes(
        text,
        args.max_tokens,
        strip_code=not args.keep_code,
        level=args.level,
        fallback=args.path.stem,
    )

    total = estimate_tokens(text)
    print(f"{args.path.name}: ~{total} tokens -> {len(episodes)} episode(s)")
    print(f"  split on H{args.level}, max {args.max_tokens} tokens per episode")
    print(f"  code blocks: {'kept' if args.keep_code else 'stripped'}")
    print(f"  target graph: {args.group_id or 'default (FALKORDB_DATABASE)'}")

    instructions = (
        None
        if args.no_extraction_instructions
        else (args.extraction_instructions or EXTRACTION_INSTRUCTIONS)
    )
    if args.no_previous_context:
        print("  prior episodes: not attached (smaller, cheaper requests)")
    else:
        print("  prior episodes: up to 10 attached to every prompt")
    if instructions is None:
        print("  extraction: default (attribute data will be dropped)")
    else:
        # Counts toward every extraction call, so it is part of the budget.
        print(
            f"  extraction: custom instructions "
            f"(+~{estimate_tokens(instructions)} tok per call)"
        )
    print()

    risky = []
    for i, (name, body) in enumerate(episodes, start=1):
        body_tokens = estimate_tokens(body)
        request_estimate = body_tokens + PROMPT_OVERHEAD_TOKENS
        flag = ""
        if request_estimate > args.tpm:
            flag = f"  <-- ~{request_estimate} tok request exceeds --tpm {args.tpm}"
            risky.append(name)
        print(f"  {i:3}. [{body_tokens:5} tok] {name}{flag}")

    if risky:
        print(
            f"\n{len(risky)} episode(s) will likely fail with HTTP 413: the body "
            f"plus ~{PROMPT_OVERHEAD_TOKENS} tokens of prompt overhead is over "
            f"your {args.tpm} TPM limit."
        )
        print(f"  lower --max-tokens (currently {args.max_tokens}) and re-check.")

    if args.dry_run:
        if args.limit:
            # The real run applies --limit after the resume filter, which
            # needs the database. Say so rather than showing a wrong plan.
            print(
                f"\n--limit {args.limit}: at run time the first {args.limit} "
                "episode(s) NOT already in the graph will be ingested."
            )
        print("\ndry run: nothing was sent to the LLM or written.")
        return 0

    # One timestamp for the whole document. Graphiti uses reference_time for
    # temporal edge invalidation, so a per-episode now() would make it treat
    # later sections as superseding earlier ones.
    reference_time = datetime.fromtimestamp(
        args.path.stat().st_mtime, tz=timezone.utc
    )
    print(f"\nreference_time: {reference_time.isoformat()}")

    # The driver must point at the group's graph, not just tag the nodes:
    # build_indices_and_constraints() has no group_id parameter and would
    # otherwise index the default graph while the data lands elsewhere.
    graphiti = make_graphiti(database=args.group_id)
    started = time.monotonic()
    nodes = edges = 0

    try:
        await graphiti.build_indices_and_constraints()

        if args.skip_existing:
            existing = await already_ingested(graphiti)
            before = len(episodes)
            episodes = [(n, b) for n, b in episodes if n not in existing]
            print(
                f"resuming: {before - len(episodes)} already in the graph, "
                f"{len(episodes)} to go"
            )

        # Applied after the resume filter on purpose: --limit 6 means "six
        # more than I already have", not "the first six of the document" --
        # which with --skip-existing would select only episodes already done.
        if args.limit:
            episodes = episodes[: args.limit]
            print(f"limited to the next {len(episodes)} episode(s) this run")

        failed = []
        for i, (name, body) in enumerate(episodes, start=1):
            print(f"\n[{i}/{len(episodes)}] {name}", flush=True)

            if args.pace and i > 1:
                await asyncio.sleep(args.pace)

            try:
                result = await add_with_retry(
                    graphiti,
                    name=name,
                    episode_body=body,
                    source=EpisodeType.text,
                    source_description=f"{args.path.name} (markdown section)",
                    reference_time=reference_time,
                    group_id=args.group_id,
                    custom_extraction_instructions=instructions,
                    # [] skips the lookup; None means "fetch the last 10".
                    previous_episode_uuids=[] if args.no_previous_context else None,
                )
            except TooLargeForTPM:
                # Keep the episodes that do fit rather than losing the run.
                print("  SKIPPED: too large for the per-minute token limit")
                failed.append(name)
                continue
            except DailyQuotaExhausted as exc:
                # Every remaining episode would fail identically, so stop now
                # instead of spending ~21 minutes of backoff on each.
                print("\n  DAILY TOKEN QUOTA EXHAUSTED -- stopping.")
                print(f"  {exc}"[:300])
                remaining = len(episodes) - i + 1
                print(
                    f"\n  {i - 1} episode(s) ingested this run, {remaining} "
                    "left. Re-run with --skip-existing once the quota resets."
                )
                break
            except RateLimitError:
                # Per-minute backoff exhausted. Skip this one, keep the run.
                print("  SKIPPED: still rate limited after all retries")
                failed.append(name)
                continue

            nodes += len(result.nodes)
            edges += len(result.edges)
            print(f"  entities: {[n.name for n in result.nodes]}")
            for edge in result.edges:
                print(f"    - {edge.fact}")
    finally:
        await graphiti.close()

    mins = (time.monotonic() - started) / 60
    print(f"\ndone: {nodes} entities, {edges} facts in {mins:.1f} min")
    if failed:
        print(f"skipped {len(failed)} oversized episode(s): {failed}")
        print(f"  re-run with a lower --max-tokens (was {args.max_tokens})")
    if args.group_id:
        print(f'search it with group "{args.group_id}" in app.py')
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
