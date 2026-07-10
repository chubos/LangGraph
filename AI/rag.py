import os
from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage, HumanMessage
from operator import add as add_messages
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langgraph.graph import StateGraph, END

load_dotenv()

llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

pdf_path = os.path.join(os.path.dirname(__file__), "Stock_Market_Performance_2024.pdf")

if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"PDF file '{pdf_path}' not found. Please ensure the file exists in the current directory.")

pdf_loader = PyPDFLoader(pdf_path)
try:
    pages = pdf_loader.load()
    print(f"Loaded {len(pages)} pages from the PDF.")
except Exception as e:
    print(f"Error loading PDF: {e}")
    raise

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

pages_split = text_splitter.split_documents(pages)

persist_directory = os.path.join(os.path.dirname(__file__), "chroma_db")
collection_name = "stock_market_performance"

if not os.path.exists(persist_directory):
    os.makedirs(persist_directory)

try:
    vectorstore = Chroma.from_documents(
        documents=pages_split,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name=collection_name
    )
    print("Created Chroma vector store.")
except Exception as e:
    print(f"Error creating Chroma vector store: {e}")
    raise

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

@tool
def retriever_tool(query: str) -> str:
    """Retrieves relevant information from the PDF based on the query."""
    docs = retriever.invoke(query)
    if not docs:
        return "No relevant information found in the document."
    
    results = []
    for i, doc in enumerate(docs):
        results.append(f"Result {i + 1}:\n{doc.page_content}\n")
    return "\n".join(results)

tools = [retriever_tool]

llm = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def should_continue(state: AgentState):
    """Check if the last message contains tool calls"""
    result = state["messages"][-1]
    return hasattr(result, "tool_calls") and len(result.tool_calls) > 0

system_prompt = """
You are an intelligent AI assistant who answers questions about Stock Market Performance in 2024 based on the PDF document loaded into your knowledge base.
Use the retriever tool available to answer questions about the stock market performance data. You can make multiple calls if needed.
If you need to look up some information before asking a follow up question, you are allowed to do that.
Please always cite the specific parts of the documents you use in your answers.  
"""

tools_dict = {our_tool.name: our_tool for our_tool in tools}

def call_llm(state: AgentState) -> AgentState:
    """Call the LLM with the current state."""
    messages = list(state["messages"])
    messages = [SystemMessage(content=system_prompt)] + messages
    message = llm.invoke(messages)
    return {"messages": [message]}

def take_action(state: AgentState) -> AgentState:
    """Take action based on the last message's tool calls."""
    tool_calls = state['messages'][-1].tool_calls
    results = []
    for t in tool_calls:
        print(f"Calling Tool: {t['name']} with query: {t['args'].get('query', 'No query provided')}")
        
        if not t['name'] in tools_dict: # Checks if a valid tool is present
            print(f"\nTool: {t['name']} does not exist.")
            result = "Incorrect Tool Name, Please Retry and Select tool from List of Available tools."
        
        else:
            result = tools_dict[t['name']].invoke(t['args'].get('query', ''))
            print(f"Result length: {len(str(result))}")
            

        # Appends the Tool Message
        results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))

    print("Tools Execution Complete. Back to the model!")
    return {'messages': results}

graph = StateGraph(AgentState)
graph.add_node("llm", call_llm)
graph.add_node("retriever_agent", take_action)

graph.add_conditional_edges("llm", should_continue, {True: "retriever_agent", False: END})

graph.add_edge("retriever_agent", "llm")
graph.set_entry_point("llm")

rag_agent = graph.compile()

def run_rag_agent():
    print("Welcome to the RAG Agent for Stock Market Performance 2024!")
    while True:
        user_input = input("Enter your question: ")
        if user_input.lower() == "exit":
            break
        
        messages = [HumanMessage(content=user_input)]
        result = rag_agent.invoke({"messages": messages})
        print("Result from RAG Agent:")
        print(f"AI: {result['messages'][-1].content}")
    
    print("Thank you for using the RAG Agent. Goodbye!")

if __name__ == "__main__":
    run_rag_agent()