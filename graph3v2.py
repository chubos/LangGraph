from typing import TypedDict, List
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    name: str
    age: str
    skills: List[str]
    final: str

def first_node(state: AgentState) -> AgentState:
    """First node of our sequence."""
    state["final"] = f"{state['name']}, Welcome to the system."
    return state

def second_node(state: AgentState) -> AgentState:
    """Second node of our sequence."""
    state["final"] = state["final"] + f" You are {state['age']} years old."
    return state

def third_node(state: AgentState) -> AgentState:
    """Third node of our sequence."""
    state["final"] = state["final"] + f" You have the following skills: {', '.join(state['skills'])}."
    return state

graph = StateGraph(AgentState)
graph.add_node("first", first_node)
graph.add_node("second", second_node)
graph.add_node("third", third_node)

graph.set_entry_point("first")
graph.add_edge("first", "second")
graph.add_edge("second", "third")
graph.set_finish_point("third")
app = graph.compile()

png = app.get_graph().draw_mermaid_png() 
with open("graph3v2.png", "wb") as f:
    f.write(png)

result =app.invoke({"name": "Linda", "age": "30", "skills": ["Python", "JavaScript"], "final": ""})
print(result["final"])
