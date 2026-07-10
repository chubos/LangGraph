from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages 
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

load_dotenv()

document_content = ""

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

@tool
def update(content: str) -> str:
    """Updates the document content."""
    global document_content
    document_content = content
    return f"Document content updated to: {document_content}"

@tool
def save(filename: str) -> str:
    """Saves the document content to a file.
    
    Args: 
    filename: Name for the text file"""
    global document_content
    if not filename.endswith(".txt"):
        filename = f"{filename}.txt"

    try:
        with open(filename, "w") as f:
            f.write(document_content)
        print(f"Document content saved to {filename}")
        return f"Document content saved to {filename}"
    except Exception as e:
        print(f"Error saving document content: {e}")
        return f"Error saving document content: {e}"
    
tools = [update, save]

model = ChatOpenAI(model_name="gpt-4.1-nano", temperature=0.7).bind_tools(tools)

def our_agent(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content=f"""You are Drafter, a helpful writing assistant. You are going to help the user update and modify documents.
                                   - If the user wants to update the document, use the 'update' tool.
                                    - If the user wants to save the document, use the 'save' tool.
                                    - Make sure to always show the current document state after modifications.
                                    
                                    Current document content: {document_content}""")
    if not state["messages"]:
        user_input = "I'm ready to help you update a document. What would you like to create?"
        user_message = HumanMessage(content=user_input)
    else:
        user_input = input("What would you like to do?")
        print(f"User input: {user_input}")
        user_message = HumanMessage(content=user_input)

    all_messages = [system_prompt] + list(state["messages"]) + [user_message]

    response = model.invoke(all_messages)
    print(f"AI: {response.content}")
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"Using tools: {[tool_call['name'] for tool_call in response.tool_calls]}")
    
    return {"messages": list(state["messages"]) + [user_message, response]}

def should_continue(state: AgentState) -> str:
    """Determines whether to continue or end the conversation."""
    messages = state["messages"]
    if not messages:
        return "continue"
    for message in reversed(messages):
        if (isinstance(message, ToolMessage) and "saved" in message.content.lower()) and "document" in message.content.lower():
            return "end"
    
    return "continue"
    
def print_messages(messages):
    """Prints the messages in a readable format."""
    if not messages:
        return
    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            print(f"Tool: {message.content}")

graph = StateGraph(AgentState)
graph.add_node("agent", our_agent)
graph.add_node("tools", ToolNode(tools=tools))

graph.set_entry_point("agent")
graph.add_edge("agent", "tools")

graph.add_conditional_edges("tools", should_continue, { "continue": "agent", "end": END })

app = graph.compile()

def run_app():
    print("Welcome to Drafter, your AI writing assistant!")

    state = {"messages": []}

    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])

    print("Thank you for using Drafter! Goodbye.")


if __name__ == "__main__":
    run_app()