from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    number1: int
    operation: str
    number2: int
    finalNumber: int

def adder(state: AgentState) -> AgentState:
    """This node adds two numbers."""
    state["finalNumber"] = state["number1"] + state["number2"]
    return state

def subtractor(state: AgentState) -> AgentState:
    """This node subtracts two numbers."""
    state["finalNumber"] = state["number1"] - state["number2"]
    return state

def decide_next_node(state: AgentState) -> AgentState:
    """This node decides which node to go to next based on the operation."""
    if state["operation"] == "+":
        return "addition_operation"
    elif state["operation"] == "-":
        return "subtraction_operation"

graph = StateGraph(AgentState)
graph.add_node("add_node", adder)
graph.add_node("subtract_node", subtractor)
graph.add_node("router", lambda state: state)

graph.add_edge(START, "router")
graph.add_conditional_edges("router", decide_next_node, {"addition_operation": "add_node", "subtraction_operation": "subtract_node"})

graph.add_edge("add_node", END)
graph.add_edge("subtract_node", END)
app = graph.compile()

png = app.get_graph().draw_mermaid_png() 
with open("graph4.png", "wb") as f:
    f.write(png)

result = app.invoke({"number1": 10, "operation": "+", "number2": 5, "finalNumber": 0})
print(result["finalNumber"])  # Should print 15
