from typing import TypedDict, Dict, List
from langgraph.graph import StateGraph, START, END
import random

class AgentState(TypedDict):
    name: str
    number: List[int]
    counter: int

def greeting_node(state: AgentState) -> AgentState:
    """This node generates a greeting message."""
    state["name"] = "Hello, " + state["name"] + "!"
    state["counter"] = 0
    return state

def random_node(state: AgentState) -> AgentState:
    """This node generates a random number from 0 to 10."""
    state["number"].append(random.randint(0, 10))
    state["counter"] += 1
    return state

def should_continue(state: AgentState) -> AgentState:
    """This node decides what to do next."""
    if state["counter"] < 5:
        print(f"Counter is {state['counter']}, continuing looping.")
        return "loop"
    else:
        return "exit"
    
graph = StateGraph(AgentState)

graph.add_node("greeting", greeting_node)
graph.add_node("random", random_node)
graph.add_edge("greeting", "random")

graph.add_conditional_edges("random", should_continue, {"loop": "random", "exit": END})

graph.set_entry_point("greeting")
app = graph.compile()

png = app.get_graph().draw_mermaid_png() 
with open("graph5.png", "wb") as f:
    f.write(png)

result = app.invoke({"name": "Alice", "number": [], "counter": -2})
print(result['number'])