import os

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
import requests
from langchain_community.tools import DuckDuckGoSearchRun

# `create_react_agent`/`AgentExecutor` moved to `langchain_classic` in langchain>=1.0;
# fall back so this runs under either the old (0.3.x) or new (1.x) langchain.
try:
    from langchain.agents import create_react_agent, AgentExecutor
except ImportError:
    from langchain_classic.agents import create_react_agent, AgentExecutor

from dotenv import load_dotenv

os.environ["LANGCHAIN_PROJECT"] = "rag chatbot1"
load_dotenv()

search_tool = DuckDuckGoSearchRun()


@tool
def get_weather_data(city: str) -> str:
    """
    This function fetches the current weather data for a given city
    """
    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1},
    ).json()
    results = geo.get("results")
    if not results:
        return f"Could not find location data for {city!r}."

    latitude = results[0]["latitude"]
    longitude = results[0]["longitude"]

    weather = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={"latitude": latitude, "longitude": longitude, "current_weather": True},
    ).json()

    return weather.get("current_weather", weather)


llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# Step 2: ReAct prompt (inlined instead of `hub.pull` so this has no dependency
# on `langchain.hub`, which was removed in langchain>=1.0)
prompt = PromptTemplate.from_template(
    """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
)

# Step 3: Create the ReAct agent manually with the pulled prompt
agent = create_react_agent(
    llm=llm, tools=[search_tool, get_weather_data], prompt=prompt
)

# Step 4: Wrap it with AgentExecutor
agent_executor = AgentExecutor(
    agent=agent,
    tools=[search_tool, get_weather_data],
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True,
)

# What is the release date of Dhadak 2?
# What is the current temp of gurgaon
# Identify the birthplace city of Kalpana Chawla (search) and give its current temperature.

# Step 5: Invoke
response = agent_executor.invoke({"input": "What is the current temp of gurgaon"})
print(response)

print(response["output"])
