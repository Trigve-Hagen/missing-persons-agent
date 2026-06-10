import os
from flask import Flask, render_template, request, jsonify
from typing import Annotated, Sequence
from typing_extensions import TypedDict

# LangChain & Ollama
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

# Chroma & RAG
from langchain_chroma import Chroma
from langchain_classic.chains import create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

# LangGraph
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# Database Imports
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

# ==========================================
# 1. DATABASE SETUP (SQLAlchemy)
# ==========================================

DATABASE_URL = "sqlite:///tasks.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Task(Base):
  __tablename__ = "tasks"

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, nullable=False)
  description = Column(String, nullable=True)
  is_completed = Column(Boolean, default=False)

# Auto-create tables on startup
Base.metadata.create_all(bind=engine)

# ==========================================
# 2. LANGCHAIN TOOL DEFINITION
# ==========================================

@tool
def create_task_row(name: str, description: str = "", is_completed: bool = False) -> str:
  """
  Creates a new task record in the tasks database.
  Use this tool whenever the user explicitly requests to create, add, or log a task.
  """
  session = SessionLocal()
  try:
    new_task = Task(name=name, description=description, is_completed=is_completed)
    session.add(new_task)
    session.commit()
    return f"Success: Task '{name}' has been created with ID {new_task.id}."
  except Exception as e:
    session.rollback()
    return f"Error creating task: {str(e)}"
  finally:
    session.close()

# Map string tool names to actual functions for safe local execution
TOOLS_MAP = {"create_task_row": create_task_row}

# ==========================================
# 3. LANGGRAPH ARCHITECTURE
# ==========================================

class ChatState(TypedDict):
  input: str
  chat_history: Annotated[Sequence, add_messages]
  context: str
  answer: str

class ChatManager:
  def __init__(self, model_name: str = "llama3", persist_dir: str = "./chroma_db"):
    # Initialize model and bind tools
    raw_llm = ChatOllama(model=model_name, temperature=0.1)
    self.llm_with_tools = raw_llm.bind_tools([create_task_row])

    self.embeddings = OllamaEmbeddings(model=model_name)

    # Connect to Chroma
    self.vector_store = Chroma(
      persist_directory=persist_dir,
      embedding_function=self.embeddings,
      collection_name="langchain"
    )
    self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 2})

    self._init_chains()
    self.graph = self._build_graph()

  def _init_chains(self):
    retriever_history_prompt = ChatPromptTemplate.from_messages([
      MessagesPlaceholder(variable_name="chat_history"),
      ("human", "{input}"),
      ("human", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
    ])
    self.history_aware_retriever = create_history_aware_retriever(
      raw_llm, self.retriever, retriever_history_prompt # Use raw model for rewriting
    )

    qa_prompt = ChatPromptTemplate.from_messages([
      ("system", "You are an assistant for question-answering and task management. Use the following documents to answer queries, or report the outcome of tool executions.\n\nContext:\n{context}"),
      MessagesPlaceholder(variable_name="chat_history"),
      ("human", "{input}"),
    ])
    self.question_answer_chain = create_stuff_documents_chain(raw_llm, qa_prompt)

  def _graph_node(self, state: ChatState):
    # Step A: Evaluate input against the tool-bound model
    # Passing history directly to help the model make routing choices
    llm_response = self.llm_with_tools.invoke([
        *state["chat_history"],
        ("human", state["input"])
    ])

    tool_outputs = []

    # Step B: Check if the model called our SQLAlchemy tool
    if llm_response.tool_calls:
      for tool_call in llm_response.tool_calls:
        tool_func = TOOLS_MAP.get(tool_call["name"])
        if tool_func:
          # Execute tool locally with parameters chosen by the AI
          result = tool_func.invoke(tool_call["args"])
          tool_outputs.append(f"Tool [{tool_call['name']}] Output: {result}")

      # Combine tool feedback so the answer generator knows what happened
      tool_context = "\n".join(tool_outputs)
      response_text = self.question_answer_chain.invoke({
        "input": state["input"],
        "chat_history": state["chat_history"],
        "context": f"Database Action Executed:\n{tool_context}"
      })
    else:
      # Step C: Fallback to standard Chroma document search if no tool is requested
      docs = self.history_aware_retriever.invoke({
        "input": state["input"],
        "chat_history": state["chat_history"]
      })
      response_text = self.question_answer_chain.invoke({
        "input": state["input"],
        "chat_history": state["chat_history"],
        "context": docs
      })

    return {
      "context": str(tool_outputs) if tool_outputs else "No tools triggered.",
      "answer": response_text,
      "chat_history": [
        ("human", state["input"]),
        ("ai", response_text)
      ]
    }

  def _build_graph(self):
    workflow = StateGraph(ChatState)
    workflow.add_node("agent", self._graph_node)
    workflow.add_edge(START, "agent")
    workflow.add_edge("agent", END)
    return workflow.compile(checkpointer=MemorySaver())

  def chat_prompt(self, user_message: str, session_id: str) -> str:
    config = {"configurable": {"thread_id": session_id}}
    output = self.graph.invoke({"input": user_message}, config=config)
    return output["answer"]

# ==========================================
# 4. FLASK ROUTER SETUP
# ==========================================

app = Flask(__name__)
# Instantiating globally for reuse across server execution cycles
raw_llm = ChatOllama(model="llama3", temperature=0.1)
chat_manager = ChatManager(model_name="llama3", persist_dir="./chroma_db")

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
  data = request.json
  user_message = data.get("message")
  session_id = data.get("session_id", "default_session")

  bot_response = chat_manager.chat_prompt(user_message, session_id)
  return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
