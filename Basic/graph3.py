from typing import TypedDict
from langgraph.graph import StateGraph
from IPython.display import display, Image

class AgentState(TypedDict):
    name: str
    age: str
    final: str

def first_node(state: AgentState) -> AgentState:
    """First node of our sequence."""
    state["final"] = f"Hello {state['name']}."
    return state

def second_node(state: AgentState) -> AgentState:
    """Second node of our sequence."""
    state["final"] = state["final"] + f" You are {state['age']} years old."
    return state

graph = StateGraph(AgentState)
graph.add_node("first", first_node)
graph.add_node("second", second_node)

graph.set_entry_point("first")
graph.add_edge("first", "second")
graph.set_finish_point("second")
app = graph.compile()

png = app.get_graph().draw_mermaid_png() 
with open("graph3.png", "wb") as f:
    f.write(png)

result =app.invoke({"name": "Bob", "age": "30", "final": ""})
print(result["final"])
