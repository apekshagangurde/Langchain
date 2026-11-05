"""
Deep Agents vs Claude Agent SDK
===============================
Two ways to build autonomous agents: different philosophies, same goal.
Deep Agents (LangChain) works with any model and focuses on orchestration; Claude Agent SDK (Anthropic) is built on the Claude Code runtime.


FEATURE COMPARISON
------------------
Feature                 | Deep Agents (LangChain)               | Claude Agent SDK (Anthropic)
------------------------|---------------------------------------|---------------------------------------------
Primary goal            | Build long-running, multi-agent       | Extend Claude Code to build powerful agents
                        | workflows                             |
Foundation              | LangChain + LangGraph                 | Claude Code infrastructure
Model support           | OpenAI, Anthropic, Gemini, Groq,      | Claude models only (Opus, Sonnet, Haiku)
                        | local models                          |
Core strength           | Multi-agent orchestration & planning  | Tool use, runtime, developer productivity
Subagents               | Native hierarchical subagents         | Subagents & delegation via Claude runtime
Context management      | Explicit context isolation &          | Managed by the Claude Code runtime
                        | quarantine                            |
Skills                  | Built-in skills system                | Skills support through the Claude ecosystem
Hooks / events          | Limited (via LangGraph workflows)     | Powerful event-driven hooks
MCP support             | Yes                                   | Yes
Multi-agent orchestr.   | Core design principle                 | Supported, but not the primary focus
Human-in-the-loop       | Via LangGraph workflows (interrupts)  | Hooks, permissions & approvals
Observability           | Native integration with LangSmith     | External (logs, tracing, etc.)
Best use cases          | Enterprise agents, RAG, research,     | Coding agents, CLI/IDE agents, DevOps,
                        | analysis, autonomous workflows        | software-engineering automation
Vendor lock-in          | Very low                              | Higher (Claude ecosystem)


ARCHITECTURE
------------
Deep Agents: hierarchical orchestration with specialised subagents and clear delegation.

                         User
                          |
                    Supervisor agent  (plans with write_todos, keeps files)
          ________________|________________________________
         |                |                |               |
   Research agent    Coding agent    Analysis agent    Docs agent
   (search, analyse  (write, review  (analyse data,    (create docs,
    and synthesise)   and test code)  create reports)   summaries)

Claude Agent SDK: runtime-first, with powerful building blocks for agents.

                         User
                          |
                Claude runtime (Claude Code)
       ___________________|____________________________
      |          |              |           |          |
    Tools      Hooks       MCP servers    Skills    Subagents
  (functions, (event-driven (connect      (reusable  (delegate tasks
   APIs,       extensibility) external     capabilities) to subagents)
   scripts)                   servers & data)


SAME AGENT, BOTH WAYS (illustrative)
------------------------------------
Deep Agents: you bring the model and the tools; the framework adds planning,
files and subagents on top (see 4_customize_deep_agent.py):

    from deepagents import create_deep_agent
    agent = create_deep_agent(model=model, tools=[get_weather], system_prompt=PROMPT)
    agent.invoke({"messages": [{"role": "user", "content": "..."}]})

Claude Agent SDK: the Claude Code runtime is the agent; you configure which
built-in tools, MCP servers, hooks and permissions it may use:

    from claude_agent_sdk import query, ClaudeAgentOptions
    options = ClaudeAgentOptions(system_prompt=PROMPT, allowed_tools=["Read", "Grep"])
    async for message in query(prompt="...", options=options):
        print(message)


WHEN TO PICK WHICH
------------------
- Pick Deep Agents when you need model freedom (e.g. Groq or local models),
  multi-agent research or analysis pipelines, and LangSmith tracing.
- Pick the Claude Agent SDK when you are building coding, CLI or DevOps agents
  on Claude and want Claude Code's ready-made tools, hooks and permissions.
"""

if __name__ == "__main__":
    print(__doc__)
