from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages: List[HumanMessage]

llm = ChatOpenAI(model_name="gpt-4.1-nano", temperature=0.7) 

def process(state: AgentState) -> AgentState:
    """This node processes the messages using the LLM."""
    response = llm.invoke(state["messages"])
    print(f"LLM Response: {response.content}")
    return state

graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()

user_input = input("Enter your message: ")
agent.invoke({"messages": [HumanMessage(content=user_input)]})
