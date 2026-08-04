from __future__ import annotations

import operator
import os
import re
from datetime import date, timedelta
from pathlib import Path
from typing import TypedDict, List, Optional, Literal, Annotated

from pydantic import BaseModel, Field, ValidationError as PydanticValidationError

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send, RetryPolicy, default_retry_on

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

# ============================================================
# Blog Writer (Router → (Research?) → Orchestrator → Workers → ReducerWithImages)
#   merge_content -> decide_images -> generate_and_place_images
#
# Changes vs. the pasted version (all verified live against this account —
# see blog_writing_agent3/4.ipynb in this folder for the debugging history):
#
# 1. Groq instead of OpenAI: `llm` (llama-3.1-8b-instant) for free-form
#    generation, `structured_llm` (openai/gpt-oss-20b, max_tokens=8000) for
#    every structured call.
# 2. method="function_calling" instead of the default. Empirically tested:
#    "json_schema" intermittently returned the schema itself instead of
#    filled-in data, or truncated mid-JSON, on this model. function_calling +
#    explicit max_tokens=8000 was reliable across repeated trials.
# 3. Task.bullets has no min_length/max_length (enforced via prompt instead) —
#    a hard constraint here caused json_validate_failed under json_schema
#    mode; kept removed since it isn't needed with function_calling either.
# 4. research_node no longer routes raw search results through an LLM
#    (EvidencePack extractor) — that hit Groq's free-tier TPM limit (413
#    rate_limit_exceeded). Evidence is normalized/deduped/date-filtered in
#    plain Python instead; Tavily already returns structured fields, so
#    there's nothing for an LLM to "extract".
# 5. RetryPolicy on every LLM node: structured_retry_policy (router,
#    orchestrator, decide_images) also retries OutputParserException/
#    pydantic ValidationError, which subclass ValueError and are otherwise
#    excluded by LangGraph's default retry policy — meaning a structured
#    parse failure would previously crash the run with zero retries.
#    llm_retry_policy (worker) tunes backoff for the 429s that show up when
#    Send() fans out several workers whose combined tokens exceed the
#    free-tier TPM limit.
# 6. Max 2 images instead of 3 (only [[IMAGE_1]]/[[IMAGE_2]] placeholders,
#    decide_images defensively slices to 2) — per free-tier Google AI Studio
#    access. Note: a live test of gemini-2.5-flash-image against this
#    account returned 429 RESOURCE_EXHAUSTED with limit: 0 — the free tier
#    currently allows ZERO image-generation requests, not fixable by asking
#    for fewer images. generate_and_place_images() already falls back to a
#    "[IMAGE GENERATION FAILED]" text note per-image instead of crashing, so
#    the run still completes and writes a usable .md file.
# ============================================================


# -----------------------------
# 1) Schemas
# -----------------------------
class Task(BaseModel):
    id: int
    title: str
    goal: str = Field(..., description="One sentence describing what the reader should do/understand.")
    bullets: List[str] = Field(..., description="3-6 concrete, non-overlapping subpoints.")
    target_words: int = Field(..., description="Target words (120-550).")

    tags: List[str] = Field(default_factory=list)
    requires_research: bool = False
    requires_citations: bool = False
    requires_code: bool = False


class Plan(BaseModel):
    blog_title: str
    audience: str
    tone: str
    blog_kind: Literal["explainer", "tutorial", "news_roundup", "comparison", "system_design"] = "explainer"
    constraints: List[str] = Field(default_factory=list)
    tasks: List[Task]


class EvidenceItem(BaseModel):
    title: str
    url: str
    published_at: Optional[str] = None  # ISO "YYYY-MM-DD" preferred
    snippet: Optional[str] = None
    source: Optional[str] = None


class RouterDecision(BaseModel):
    needs_research: bool
    mode: Literal["closed_book", "hybrid", "open_book"]
    reason: str
    queries: List[str] = Field(default_factory=list)
    max_results_per_query: int = Field(5)


# ---- Image planning schema ----
# NOTE: earlier versions had the model echo back the ENTIRE merged markdown
# with placeholders inserted (md_with_placeholders). For a real 5-9 section
# blog that's several thousand tokens of near-verbatim repetition just to
# place 1-2 images — it reliably truncated mid-JSON (400 tool_use_failed,
# "Failed to parse tool call arguments as JSON"), confirmed on a live run.
# Instead, the model only returns which section each image follows
# (after_section); the placement itself is done in plain Python.
class ImageSpec(BaseModel):
    after_section: str = Field(
        ..., description="Exact text of the ## section heading this image should follow (without the '##')."
    )
    filename: str = Field(..., description="Save under images/, e.g. qkv_flow.png")
    alt: str
    caption: str
    prompt: str = Field(..., description="Prompt to send to the image model.")
    size: Literal["1024x1024", "1024x1536", "1536x1024"] = "1024x1024"
    quality: Literal["low", "medium", "high"] = "medium"


class GlobalImagePlan(BaseModel):
    images: List[ImageSpec] = Field(default_factory=list)


class State(TypedDict):
    topic: str

    # routing / research
    mode: str
    needs_research: bool
    queries: List[str]
    evidence: List[EvidenceItem]
    plan: Optional[Plan]

    # recency
    as_of: str
    recency_days: int

    # workers
    sections: Annotated[List[tuple[int, str]], operator.add]  # (task_id, section_md)

    # reducer/image
    merged_md: str
    image_specs: List[dict]

    final: str


# -----------------------------
# 2) LLM
# -----------------------------
llm = ChatGroq(model="llama-3.1-8b-instant")

# llama-3.1-8b-instant doesn't support structured-output methods on Groq, so a
# separate model handles every structured-output call below. No max_tokens
# override: tested 5/5 reliable on the largest schema (Plan, 7 sections)
# both with and without one — an earlier override (max_tokens=8000) actually
# caused its own 413 (it reserves the full free-tier 8000 TPM/minute budget
# for the completion alone, leaving no room for the prompt).
structured_llm = ChatGroq(model="openai/gpt-oss-20b")


# OutputParserException / pydantic ValidationError both subclass ValueError,
# which LangGraph's default_retry_on explicitly excludes from retries — so a
# structured-output parse failure would otherwise crash the whole run with
# ZERO retries. Retry those too, on top of the default behavior (which
# already retries groq.RateLimitError/BadRequestError etc.).
def structured_retry_on(exc: Exception) -> bool:
    if isinstance(exc, (OutputParserException, PydanticValidationError)):
        return True
    return default_retry_on(exc)


structured_retry_policy = RetryPolicy(
    max_attempts=5, initial_interval=5, backoff_factor=2.0, max_interval=30, retry_on=structured_retry_on
)

# worker has no structured output to parse — this just tunes backoff to match
# Groq's free-tier "please try again in Ns" TPM windows.
llm_retry_policy = RetryPolicy(max_attempts=5, initial_interval=10, backoff_factor=2.0, max_interval=60)

# -----------------------------
# 3) Router
# -----------------------------
ROUTER_SYSTEM = """You are a routing module for a technical blog planner.

Decide whether web research is needed BEFORE planning.

Modes:
- closed_book (needs_research=false): evergreen concepts.
- hybrid (needs_research=true): evergreen + needs up-to-date examples/tools/models.
- open_book (needs_research=true): volatile weekly/news/"latest"/pricing/policy.

If needs_research=true:
- Output 3-6 high-signal, scoped queries.
- For open_book weekly roundup, include queries reflecting last 7 days.
"""

def router_node(state: State) -> dict:
    decider = structured_llm.with_structured_output(RouterDecision, method="function_calling")
    decision = decider.invoke(
        [
            SystemMessage(content=ROUTER_SYSTEM),
            HumanMessage(content=f"Topic: {state['topic']}\nAs-of date: {state['as_of']}"),
        ]
    )

    if decision.mode == "open_book":
        recency_days = 7
    elif decision.mode == "hybrid":
        recency_days = 45
    else:
        recency_days = 3650

    return {
        "needs_research": decision.needs_research,
        "mode": decision.mode,
        "queries": decision.queries[:6],
        "recency_days": recency_days,
    }

def route_next(state: State) -> str:
    return "research" if state["needs_research"] else "orchestrator"

# -----------------------------
# 4) Research (Tavily) — normalized/deduped/date-filtered in plain Python,
# no LLM call (see note at top of file for why).
# -----------------------------
def _tavily_search(query: str, max_results: int = 4) -> List[dict]:
    if not os.getenv("TAVILY_API_KEY"):
        return []
    try:
        from langchain_community.tools.tavily_search import TavilySearchResults  # type: ignore
        tool = TavilySearchResults(max_results=max_results)
        results = tool.invoke({"query": query})
        out: List[dict] = []
        for r in results or []:
            snippet = r.get("content") or r.get("snippet") or ""
            out.append(
                {
                    "title": r.get("title") or "",
                    "url": r.get("url") or "",
                    "snippet": snippet[:300],
                    "published_at": r.get("published_date") or r.get("published_at"),
                    "source": r.get("source"),
                }
            )
        return out
    except Exception:
        return []

def _iso_to_date(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    try:
        return date.fromisoformat(s[:10])
    except Exception:
        return None

def research_node(state: State) -> dict:
    queries = (state.get("queries") or [])[:6]
    raw: List[dict] = []
    for q in queries:
        raw.extend(_tavily_search(q, max_results=4))

    if not raw:
        return {"evidence": []}

    dedup: dict[str, EvidenceItem] = {}
    for r in raw:
        if r["url"] and r["url"] not in dedup:
            dedup[r["url"]] = EvidenceItem(**r)
    evidence = list(dedup.values())[:16]

    if state.get("mode") == "open_book":
        as_of = date.fromisoformat(state["as_of"])
        cutoff = as_of - timedelta(days=int(state["recency_days"]))
        evidence = [e for e in evidence if (d := _iso_to_date(e.published_at)) and d >= cutoff]

    return {"evidence": evidence}

# -----------------------------
# 5) Orchestrator (Plan)
# -----------------------------
ORCH_SYSTEM = """You are a senior technical writer and developer advocate.
Produce a highly actionable outline for a technical blog post.

Requirements:
- 5-9 tasks, each with goal + 3-6 bullets + target_words.
- Tags are flexible; do not force a fixed taxonomy.

Grounding:
- closed_book: evergreen, no evidence dependence.
- hybrid: use evidence for up-to-date examples; mark those tasks requires_research=True and requires_citations=True.
- open_book: weekly/news roundup:
  - Set blog_kind="news_roundup"
  - No tutorial content unless requested
  - If evidence is weak, plan should explicitly reflect that (don't invent events).

Output must match Plan schema.
"""

def orchestrator_node(state: State) -> dict:
    planner = structured_llm.with_structured_output(Plan, method="function_calling")
    mode = state.get("mode", "closed_book")
    evidence = state.get("evidence", [])

    forced_kind = "news_roundup" if mode == "open_book" else None

    plan = planner.invoke(
        [
            SystemMessage(content=ORCH_SYSTEM),
            HumanMessage(
                content=(
                    f"Topic: {state['topic']}\n"
                    f"Mode: {mode}\n"
                    f"As-of: {state['as_of']} (recency_days={state['recency_days']})\n"
                    f"{'Force blog_kind=news_roundup' if forced_kind else ''}\n\n"
                    f"Evidence:\n{[e.model_dump() for e in evidence][:16]}"
                )
            ),
        ]
    )
    if forced_kind:
        plan.blog_kind = "news_roundup"

    return {"plan": plan}


# -----------------------------
# 6) Fanout
# -----------------------------
def fanout(state: State):
    assert state["plan"] is not None
    return [
        Send(
            "worker",
            {
                "task": task.model_dump(),
                "topic": state["topic"],
                "mode": state["mode"],
                "as_of": state["as_of"],
                "recency_days": state["recency_days"],
                "plan": state["plan"].model_dump(),
                "evidence": [e.model_dump() for e in state.get("evidence", [])],
            },
        )
        for task in state["plan"].tasks
    ]

# -----------------------------
# 7) Worker
# -----------------------------
WORKER_SYSTEM = """You are a senior technical writer and developer advocate.
Write ONE section of a technical blog post in Markdown.

Constraints:
- Cover ALL bullets in order.
- Target words ±15%.
- Output only section markdown starting with "## <Section Title>".

Scope guard:
- If blog_kind=="news_roundup", do NOT drift into tutorials (scraping/RSS/how to fetch).
  Focus on events + implications.

Grounding:
- If mode=="open_book": do not introduce any specific event/company/model/funding/policy claim unless supported by provided Evidence URLs.
  For each supported claim, attach a Markdown link ([Source](URL)).
  If unsupported, write "Not found in provided sources."
- If requires_citations==true (hybrid tasks): cite Evidence URLs for external claims.

Code:
- If requires_code==true, include at least one minimal snippet.
"""

def worker_node(payload: dict) -> dict:
    task = Task(**payload["task"])
    plan = Plan(**payload["plan"])
    evidence = [EvidenceItem(**e) for e in payload.get("evidence", [])]

    bullets_text = "\n- " + "\n- ".join(task.bullets)
    evidence_text = "\n".join(
        f"- {e.title} | {e.url} | {e.published_at or 'date:unknown'}"
        for e in evidence[:20]
    )

    section_md = llm.invoke(
        [
            SystemMessage(content=WORKER_SYSTEM),
            HumanMessage(
                content=(
                    f"Blog title: {plan.blog_title}\n"
                    f"Audience: {plan.audience}\n"
                    f"Tone: {plan.tone}\n"
                    f"Blog kind: {plan.blog_kind}\n"
                    f"Constraints: {plan.constraints}\n"
                    f"Topic: {payload['topic']}\n"
                    f"Mode: {payload.get('mode')}\n"
                    f"As-of: {payload.get('as_of')} (recency_days={payload.get('recency_days')})\n\n"
                    f"Section title: {task.title}\n"
                    f"Goal: {task.goal}\n"
                    f"Target words: {task.target_words}\n"
                    f"Tags: {task.tags}\n"
                    f"requires_research: {task.requires_research}\n"
                    f"requires_citations: {task.requires_citations}\n"
                    f"requires_code: {task.requires_code}\n"
                    f"Bullets:{bullets_text}\n\n"
                    f"Evidence (ONLY cite these URLs):\n{evidence_text}\n"
                )
            ),
        ]
    ).content.strip()

    return {"sections": [(task.id, section_md)]}

# ============================================================
# 8) ReducerWithImages (subgraph)
#    merge_content -> decide_images -> generate_and_place_images
# ============================================================
def merge_content(state: State) -> dict:
    plan = state["plan"]
    if plan is None:
        raise ValueError("merge_content called without plan.")
    ordered_sections = [md for _, md in sorted(state["sections"], key=lambda x: x[0])]
    body = "\n\n".join(ordered_sections).strip()
    merged_md = f"# {plan.blog_title}\n\n{body}\n"
    return {"merged_md": merged_md}


# Capped at 2 images (free-tier Google AI Studio access) instead of 3.
DECIDE_IMAGES_SYSTEM = """You are an expert technical editor.
Decide if images/diagrams are needed for THIS blog.

Rules:
- Max 2 images total.
- Each image must materially improve understanding (diagram/flow/table-like visual).
- For each image, set after_section to the EXACT text of the ## heading it
  should follow (copy it verbatim from the document, without the '##').
- If no images needed, return images=[].
- Avoid decorative images; prefer technical diagrams with short labels.
- Do NOT reproduce or repeat the blog content back — only return the image specs.
Return strictly GlobalImagePlan.
"""

def decide_images(state: State) -> dict:
    planner = structured_llm.with_structured_output(GlobalImagePlan, method="function_calling")
    merged_md = state["merged_md"]
    plan = state["plan"]
    assert plan is not None

    image_plan = planner.invoke(
        [
            SystemMessage(content=DECIDE_IMAGES_SYSTEM),
            HumanMessage(
                content=(
                    f"Blog kind: {plan.blog_kind}\n"
                    f"Topic: {state['topic']}\n\n"
                    "Propose up to 2 images for this document (do not repeat the document back):\n\n"
                    f"{merged_md}"
                )
            ),
        ]
    )

    # defensive cap in case the model over-proposes
    images = image_plan.images[:2]

    return {
        "image_specs": [img.model_dump() for img in images],
    }


HF_IMAGE_MODEL = "stabilityai/stable-diffusion-3-medium-diffusers"


def _generate_image_bytes(prompt: str) -> bytes:
    """
    Returns raw image bytes generated via Hugging Face's Inference API.
    Env var: HUGGINGFACEHUB_API_TOKEN (free — https://huggingface.co/settings/tokens,
    no billing/card required for this).

    Swapped in for Gemini: gemini-2.5-flash-image is a real, callable model,
    but a live test against a free-tier Google AI Studio key returned 429
    RESOURCE_EXHAUSTED with limit: 0 — the free tier currently allows ZERO
    image-generation requests, so it would always fail here. HF's free
    Inference API was verified live (this call, this token) to return actual
    image bytes with no billing involved.

    Cold-start handling: the first call to a model can 503 with
    "loading, estimated_time: Ns" while HF spins up the model — retried a
    few times rather than treated as a hard failure.
    """
    import time

    import requests

    token = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    if not token:
        raise RuntimeError("HUGGINGFACEHUB_API_TOKEN is not set.")

    url = f"https://router.huggingface.co/hf-inference/models/{HF_IMAGE_MODEL}"
    headers = {"Authorization": f"Bearer {token}"}

    last_error = None
    for attempt in range(4):
        resp = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=60)
        content_type = resp.headers.get("content-type", "")

        if resp.status_code == 200 and "image" in content_type:
            return resp.content

        if resp.status_code == 503:
            # model is cold-starting — wait and retry
            wait_s = 20
            try:
                wait_s = min(30, float(resp.json().get("estimated_time", wait_s)))
            except Exception:
                pass
            last_error = f"503 (cold start), retrying in {wait_s:.0f}s"
            time.sleep(wait_s)
            continue

        last_error = f"{resp.status_code}: {resp.text[:300]}"
        break

    raise RuntimeError(f"HF image generation failed: {last_error}")


def _safe_slug(title: str) -> str:
    s = title.strip().lower()
    s = re.sub(r"[^a-z0-9 _-]+", "", s)
    s = re.sub(r"\s+", "_", s).strip("_")
    return s or "blog"


def _insert_after_section(md: str, section_title: str, snippet: str) -> str:
    """Insert `snippet` right before the next `## ` heading after the one
    matching `section_title` (i.e. at the end of that section). Falls back
    to appending at the very end of the doc if no heading matches."""
    lines = md.split("\n")
    target = section_title.strip().lower()

    start_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#") and stripped.lstrip("#").strip().lower() == target:
            start_idx = i
            break

    if start_idx is None:
        return md.rstrip("\n") + f"\n\n{snippet}\n"

    end_idx = len(lines)
    for j in range(start_idx + 1, len(lines)):
        if lines[j].strip().startswith("## "):
            end_idx = j
            break

    new_lines = lines[:end_idx] + ["", snippet, ""] + lines[end_idx:]
    return "\n".join(new_lines)


def generate_and_place_images(state: State) -> dict:
    plan = state["plan"]
    assert plan is not None

    md = state["merged_md"]
    image_specs = state.get("image_specs", []) or []

    # If no images requested, just write merged markdown
    if not image_specs:
        filename = f"{_safe_slug(plan.blog_title)}.md"
        Path(filename).write_text(md, encoding="utf-8")
        return {"final": md}

    images_dir = Path("images")
    images_dir.mkdir(exist_ok=True)

    for spec in image_specs:
        filename = spec["filename"]
        out_path = images_dir / filename

        # generate only if needed
        if not out_path.exists():
            try:
                img_bytes = _generate_image_bytes(spec["prompt"])
                out_path.write_bytes(img_bytes)
                img_md = f"![{spec['alt']}](images/{filename})\n*{spec['caption']}*"
            except Exception as e:
                # graceful fallback: keep doc usable
                img_md = (
                    f"> **[IMAGE GENERATION FAILED]** {spec.get('caption','')}\n>\n"
                    f"> **Alt:** {spec.get('alt','')}\n>\n"
                    f"> **Prompt:** {spec.get('prompt','')}\n>\n"
                    f"> **Error:** {e}\n"
                )
        else:
            img_md = f"![{spec['alt']}](images/{filename})\n*{spec['caption']}*"

        md = _insert_after_section(md, spec.get("after_section", ""), img_md)

    filename = f"{_safe_slug(plan.blog_title)}.md"
    Path(filename).write_text(md, encoding="utf-8")
    return {"final": md}

# build reducer subgraph
reducer_graph = StateGraph(State)
reducer_graph.add_node("merge_content", merge_content)
reducer_graph.add_node("decide_images", decide_images, retry_policy=structured_retry_policy)
reducer_graph.add_node("generate_and_place_images", generate_and_place_images)
reducer_graph.add_edge(START, "merge_content")
reducer_graph.add_edge("merge_content", "decide_images")
reducer_graph.add_edge("decide_images", "generate_and_place_images")
reducer_graph.add_edge("generate_and_place_images", END)
reducer_subgraph = reducer_graph.compile()

# -----------------------------
# 9) Build main graph
# -----------------------------
g = StateGraph(State)
g.add_node("router", router_node, retry_policy=structured_retry_policy)
g.add_node("research", research_node)
g.add_node("orchestrator", orchestrator_node, retry_policy=structured_retry_policy)
g.add_node("worker", worker_node, retry_policy=llm_retry_policy)
g.add_node("reducer", reducer_subgraph)

g.add_edge(START, "router")
g.add_conditional_edges("router", route_next, {"research": "research", "orchestrator": "orchestrator"})
g.add_edge("research", "orchestrator")

g.add_conditional_edges("orchestrator", fanout, ["worker"])
g.add_edge("worker", "reducer")
g.add_edge("reducer", END)

app = g.compile()

# -----------------------------
# 10) Runner
# -----------------------------
def run(topic: str, as_of: Optional[str] = None):
    if as_of is None:
        as_of = date.today().isoformat()

    out = app.invoke(
        {
            "topic": topic,
            "mode": "",
            "needs_research": False,
            "queries": [],
            "evidence": [],
            "plan": None,
            "as_of": as_of,
            "recency_days": 7,
            "sections": [],
            "merged_md": "",
            "image_specs": [],
            "final": "",
        }
    )

    return out


if __name__ == "__main__":
    result = run("Self Attention in Transformer Architecture")
    print(result["final"])
