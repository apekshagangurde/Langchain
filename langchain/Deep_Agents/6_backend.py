"""
Backend
=======

WHAT IS A BACKEND?
------------------
A backend is the storage layer behind a deep agent's file system. It decides
WHERE the agent's files actually live when it calls its built-in file tools
(ls, read_file, write_file, edit_file, glob, grep).

The agent always uses the same tools; the backend just changes where the files
are kept. You choose one with `create_deep_agent(..., backend=...)`. If you pass
nothing, the default is `StateBackend`.


DIFFERENT BACKENDS (from deepagents.backends)
---------------------------------------------
1. StateBackend        (default) Files live in the agent's LangGraph state.
                       Ephemeral: they last for one thread/conversation only.

2. StoreBackend        Files live in a LangGraph Store (BaseStore).
                       Persistent: they survive across threads/conversations.

3. FilesystemBackend   Reads and writes real files on your disk, under a
                       `root_dir` you choose.

4. CompositeBackend    A router: sends each path prefix to a different backend,
                       e.g. "/memories/" -> StoreBackend, everything else -> StateBackend.

5. LocalShellBackend   FilesystemBackend plus an `execute` tool that runs shell
                       commands on your machine, with no restrictions. Use with care.

6. ContextHubBackend   Files live in a LangSmith Hub agent repo (persistent).

7. LangSmithSandbox    A remote LangSmith sandbox: files plus safe, isolated
                       command execution.

Custom backends: any class that implements `BackendProtocol` (ls, read, write,
edit, grep, glob, ...) can be used as a backend.
"""


# ---------------------------------------------------------------------------
# SIMPLE EXAMPLE: StateBackend
# The agent writes a note with `write_file`. With StateBackend that file is not
# on your disk: it lives in the agent's state, and we read it back from
# result["files"] after the run.
# ---------------------------------------------------------------------------
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend, StateBackend
from dotenv import load_dotenv
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_groq import ChatGroq

load_dotenv()

# Rate limiter keeps us under Groq's free-tier tokens/minute cap.
model = ChatGroq(
    model="openai/gpt-oss-120b",
    rate_limiter=InMemoryRateLimiter(requests_per_second=0.04, check_every_n_seconds=0.5),
)

agent = create_deep_agent(
    model=model,
    backend=StateBackend(),  # same as the default; written out to make it explicit
    system_prompt="You are a note-taking assistant. Save notes with `write_file`.",
)


# ---------------------------------------------------------------------------
# SIMPLE EXAMPLE: FilesystemBackend
# Same agent, but now `write_file` creates a REAL file on your disk, inside
# `root_dir`. virtual_mode=True makes "/" mean root_dir, so the agent's
# "/notes/pune.md" becomes ./agent_files/notes/pune.md and it cannot write
# anywhere outside that folder.
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).parent / "agent_files"
ROOT_DIR.mkdir(exist_ok=True)

fs_agent = create_deep_agent(
    model=model,
    backend=FilesystemBackend(root_dir=ROOT_DIR, virtual_mode=True),
    system_prompt="You are a note-taking assistant. Save notes with `write_file`.",
)

if __name__ == "__main__":
    print("=" * 20, "StateBackend", "=" * 20)
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Save a 2-line note about Pune to /notes/pune.md, then say done.",
                }
            ]
        }
    )

    print("Agent reply:", result["messages"][-1].content)

    # Files written by the agent live in state, not on disk.
    print("\nFiles in state:")
    for path, file_data in result.get("files", {}).items():
        print(f"--- {path} ---")
        print(file_data["content"])

    print("\n" + "=" * 20, "FilesystemBackend", "=" * 20)
    fs_result = fs_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Save a 2-line note about Mumbai to /notes/mumbai.md, then say done.",
                }
            ]
        }
    )

    print("Agent reply:", fs_result["messages"][-1].content)

    # Files written by the agent are real files on disk now.
    print(f"\nFiles on disk under {ROOT_DIR}:")
    for file_path in ROOT_DIR.rglob("*"):
        if file_path.is_file():
            print(f"--- {file_path.relative_to(ROOT_DIR)} ---")
            print(file_path.read_text())
