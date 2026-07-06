from typing import List, TypedDict
from langgraph.graph import StateGraph
from IPython.display import display, Image

class AgentState(TypedDict):
    values: List[int]
    name: str
    result: str


def process_values(state: AgentState) -> AgentState:
    """Node that processes a list of values."""
    state["result"] = f"Hi {state['name']}, the sum of your values is {sum(state['values'])}."
    return state

graph = StateGraph(AgentState)
graph.add_node("processor", process_values)
graph.set_entry_point("processor")
graph.set_finish_point("processor")

app = graph.compile()

png = app.get_graph().draw_mermaid_png() 
with open("graph2.png", "wb") as f:
    f.write(png)

answer = app.invoke({"values": [1, 2, 3], "name": "Alice", "result": ""})
print(answer)