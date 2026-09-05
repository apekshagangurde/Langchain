"""
ModelFallbackMiddleware
=======================
If the primary model fails — rate limit, outage, retired model id — the agent
normally crashes. `ModelFallbackMiddleware` catches the failure and retries the
same request on backup models, in the order you list them.

    ModelFallbackMiddleware(first_backup, second_backup, ...)

    primary (from create_agent) fails -> try first_backup
    first_backup fails                -> try second_backup
    all fail                          -> the last error is raised

The primary model stays the one you pass to `create_agent(model=...)`.
The middleware only lists what to fall back TO.
"""

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware
from langchain_groq import ChatGroq

load_dotenv()

# A deliberately broken primary so the fallback actually fires in this demo.
primary = ChatGroq(model="this-model-does-not-exist")

agent = create_agent(
    model=primary,
    system_prompt="You are a helpful assistant. Answer in one sentence.",
    middleware=[
        ModelFallbackMiddleware(
            ChatGroq(model="openai/gpt-oss-20b"),   # tried first when primary fails
            ChatGroq(model="openai/gpt-oss-120b"),  # tried if that one fails too
        )
    ],
)

result = agent.invoke({"messages": [{"role": "user", "content": "What is LangChain?"}]})

print(result["messages"][-1].text)
print("\nThe primary model 404'd, so the fallback model answered instead.")
