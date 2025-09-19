from ast import parse
from typing import Annotated
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import os

load_dotenv()

base_url = os.getenv("BASE_URL")


# ----------------------------------Tools----------------------------------
@tool()
def get_weather(location: Annotated[str, "the location to query"]) -> str:
    """Query the weather of a given location
       Return a string of weather description
    """
    return f"The weather in {location} is always sunny!"


tools = [get_weather]

tool_map = {"get_weather": get_weather}


# ----------------------------------Pydantic Models----------------------------------
class RecommendedAnime(BaseModel):
    anime_name: str = Field(description="the name of the recommended anime")
    recommend_reason: str =Field(description="the reason for recommending the anime")


class Recommendation(BaseModel):
    anime_list: list[RecommendedAnime] = Field(description="a list of recommended anime item, each item is a 'RecommendedAnime' class")


# ----------------------------------model----------------------------------

# llm = init_chat_model("openai/gpt-4.1-mini", model_provider="openai")
llm = ChatOpenAI(model="openai/gpt-4.1-mini", temperature=0.5)
llm_with_tools = llm.bind_tools(tools)


# ----------------------------------memory----------------------------------
# messages = [
#     SystemMessage(content="Translate the following from English into Italian"),
#     HumanMessage(content="hi!"),
# ]

# response = model.invoke(messages)
# print(response.content)

# ----------------------------------prompts----------------------------------
system_template = """
    You are a helpful assistant for recommending anime based on user's preferrence. 
    After receiving user input anime and analysing them, Give 5 recommendation that suit the user best
"""

prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)

prompt = prompt_template.invoke(
    {"text": "鬼灭之刃，咒术回战，月色真美，从零开始的异世界生活，四月是你的谎言"}
)

messages = prompt.to_messages()


# ----------------------------------Execution----------------------------------
messages = [HumanMessage("What's the weather in Shanghai?")]
ai_msg = llm_with_tools.invoke(messages)
messages.append(ai_msg)

for tool_call in ai_msg.tool_calls:
    selected_tool = tool_map[tool_call["name"].lower()]
    tool_msg = selected_tool.invoke(tool_call)
    messages.append(tool_msg)

# print(messages)

# response = llm_with_tools.with_structured_output(Recommendation).invoke(messages)
response = llm_with_tools.invoke(messages)
print(response.content)

# print(get_weather.args_schema.model_json_schema())







