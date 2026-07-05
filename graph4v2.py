from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    number1: int
    operation: str
    number2: int
    operation2:str
    number3: int
    number4:int
    finalNumber: int
    finalNumber2:int

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
    
def adder2(state: AgentState) -> AgentState:
    """This node adds two numbers."""
    state["finalNumber2"] = state["number3"] + state["number4"]
    return state

def subtractor2(state: AgentState) -> AgentState:
    """This node subtracts two numbers."""
    state["finalNumber2"] = state["number3"] - state["number4"]
    return state

def decide_next_node2(state: AgentState) -> AgentState:
    """This node decides which node to go to next based on the operation."""
    if state["operation2"] == "+":
        return "addition_operation2"
    elif state["operation2"] == "-":
        return "subtraction_operation2"

graph = StateGraph(AgentState)
graph.add_node("add_node", adder)
graph.add_node("subtract_node", subtractor)
graph.add_node("router", lambda state: state)

graph.add_node("add_node2", adder2)
graph.add_node("subtract_node2", subtractor2)
graph.add_node("router2", lambda state: state)

graph.add_edge(START, "router")
graph.add_conditional_edges("router", decide_next_node, {"addition_operation": "add_node", "subtraction_operation": "subtract_node"})

graph.add_edge("add_node", "router2")
graph.add_edge("subtract_node", "router2")

graph.add_conditional_edges("router2", decide_next_node2, {"addition_operation2": "add_node2", "subtraction_operation2": "subtract_node2"})

graph.add_edge("add_node2", END)
graph.add_edge("subtract_node2", END)
app = graph.compile()

png = app.get_graph().draw_mermaid_png() 
with open("graph4v2.png", "wb") as f:
    f.write(png)

result = app.invoke({"number1": 10, "operation": "+", "number2": 5, "number3": 20, "operation2": "-", "number4": 10, "finalNumber": 0, "finalNumber2": 0})
print(result["finalNumber"])  # Should print 15
print(result["finalNumber2"])  # Should print 10
