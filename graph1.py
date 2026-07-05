from typing import Dict, TypedDict
from langgraph.graph import StateGraph
from IPython.display import display, Image


class AgentState(TypedDict):
    message: str

def greeting_agent(state: AgentState) -> AgentState:
    """Simple node that adds a greeting message to the state."""
    state["message"] = "Hello! " + state["message"] + " How can I assist you today?"
    return state

graph = StateGraph(AgentState)
graph.add_node("greeter",greeting_agent)
graph.set_entry_point("greeter")
graph.set_finish_point("greeter")

app = graph.compile()

png = app.get_graph().draw_mermaid_png() 
with open("graph.png", "wb") as f:
    f.write(png)

result = app.invoke({"message": "Charlie"})
print(result)
print(result['message'])