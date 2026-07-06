from typing import TypedDict, List, Union
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

class AgentState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]

llm = ChatOpenAI(model_name="gpt-4.1-nano", temperature=0.7) 

def process(state: AgentState) -> AgentState:
    """This node processes the request you input."""
    response = llm.invoke(state["messages"])
    print(f"AI: {response.content}")
    state["messages"].append(AIMessage(content=response.content))
    return state

graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()

conversation_history = []

user_input = input("Enter your message: ")
while user_input.lower() != "exit":
    conversation_history.append(HumanMessage(content=user_input))
    result = agent.invoke({"messages": conversation_history})

    conversation_history = result["messages"]
    user_input = input("Enter your message (or type 'exit' to quit): ")

with open("graph2.txt", "w") as f:
    for message in conversation_history:
        if isinstance(message, HumanMessage):
            f.write(f"Human: {message.content}\n")
        elif isinstance(message, AIMessage):
            f.write(f"AI: {message.content}\n")
        f.write("End of conversation\n\n")
print("Conversation history saved to graph2.txt")
