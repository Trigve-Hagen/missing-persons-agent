import os
import json
from ollama import chat
from flask import flash
from sqlalchemy import select
from database.person import Person
from database.model import Model, Prompt, Question
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Annotated, Sequence, TypedDict
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_classic.chains import create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from classes.model_utils import ModelUtils
from classes.chroma_database import ChromaDatabase
from classes.tools import get_current_weather
from datetime import datetime
from langchain_core.tools import tool

# LangGraph imports
from typing import Annotated, Sequence
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage
from langchain_core.callbacks import BaseCallbackHandler

# ---------------------------------------------------------
# Agent Logs
# ---------------------------------------------------------

class AgentLogHandler(BaseCallbackHandler):
  def __init__(self, log_file=ModelUtils.resource_path(os.path.join("logs", "errors.log"))):
    self.log_file = log_file

  def on_llm_start(self, serialized, prompts, **kwargs):
    """Logs when the Ollama LLM begins processing."""
    self._write_log(f"[LLM START] Prompts: {prompts}")

  def on_agent_action(self, action, **kwargs):
    """Logs the specific tool the agent decided to call."""
    self._write_log(f"[AGENT ACTION] Tool: {action.tool} | Input: {action.tool_input}")

  def on_tool_end(self, output, **kwargs):
    """Logs the resulting output from the tool execution."""
    self._write_log(f"[TOOL RESULT] Output: {output}")

  def on_llm_end(self, response, **kwargs):
    """Logs the final text generation from the LLM."""
    self._write_log(f"[LLM END] Response: {response.generations[0][0].text}")

  def _write_log(self, text):
    with open(self.log_file, "a", encoding="utf-8") as f:
      f.write(text + "\n\n")

# Attach the custom logger when invoking your agent
# log_handler = AgentLogHandler()
# agent_executor.invoke(
#     {"input": "Calculate 456 * 77"},
#     config={"callbacks": [log_handler]}
# )

# ---------------------------------------------------------
# Pydantic Schemas for Structured LLM Output
# ---------------------------------------------------------

class Task(BaseModel):
    name: str = Field(..., description="The name of the task.")
    sql_table_name: str = Field(..., description="The name of the SQL table where the data fits best.")
    sql_insert_statement: str = Field(..., description="The exact raw SQL INSERT statement to execute.")
    if_complete: int = Field(default=0, description="Default to 0.")
    dateCreated: datetime = Field(default_factory=datetime.now)
    dateCompleted: Optional[datetime] = Field(default=None)

# ---------------------------------------------------------
# State
# ---------------------------------------------------------

class AgentState(TypedDict):
  messages: Annotated[Sequence[BaseMessage], add_messages]

# ---------------------------------------------------------
# LLMs
# ---------------------------------------------------------

class ToolsLlms:
  def __init__(self):
    self.tools = self.get_tools()

    self.llm = ChatOllama(
      model="qwen3.5:latest",
      temperature=0.1,
      num_ctx=2048
    ).bind_tools(tools=self.tools)

    self.conversation_history = []

    self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    self.vector_store = Chroma(
      persist_directory=ModelUtils.resource_path(os.path.join("database", "investigation_db")),
      embedding_function=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"),
      collection_name="missing_persons"
    )
    self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

    self.agent = self.build_graph()

  # ---------------------------------------------------------
  # Tools
  # ---------------------------------------------------------

  def get_tools(self):

    @tool
    def add(a: int, b: int):
      """ Adds two numbers. """
      return a + b

    @tool
    def multiply(a: int, b: int):
      """ Multiplies two numbers. """
      return a * b

    return [add, multiply]

  def model_call(self, state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content="You are my AI assistant, please answer my query to the best of your ability.")
    response = self.llm.invoke([system_prompt] + state['messages'])
    return {"messages": [response]}

  def should_continue(self, state: AgentState):
    messages = state['messages']
    last_message = messages[-1]
    if not last_message.tool_calls:
      return "end"
    else:
      return "continue"

  def process(self, state: AgentState) -> AgentState:
    response = self.llm.invoke(state['messages'])
    state['messages'].append(AIMessage(content=response.content))
    print(f"\nAI: {response.content}")
    print("CURRENT STATE: ", state['messages'])
    return state

  def do_build_graph(self):
    graph = StateGraph(AgentState)
    graph.add_node("process", self.process)
    graph.add_edge(START, "process")
    graph.add_edge("process", END)

    return graph.compile()

  def build_graph(self):
    graph = StateGraph(AgentState)
    graph.add_node("our_agent", self.model_call)

    tool_node = ToolNode(tools=self.tools)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("our_agent")

    graph.add_conditional_edges(
      "our_agent",
      self.should_continue,
      {
        "continue": "tools",
        "end": END
      },
    )

    graph.add_edge("tools", "our_agent")

    return graph.compile()

  def invoke(self):
    user_input = input("Enter: ")
    while user_input != "exit":
      self.conversation_history.append(HumanMessage(content=user_input))
      result = self.agent.invoke({"messages": self.conversation_history})
      print(result["messages"])
      self.conversation_history = result["messages"]
      user_input = input("Enter: ")

  def print_stream(self, stream):
    for s in stream:
      message = s["messages"][-1]
      if isinstance(message, tuple):
        print(message)
      else:
        message.pretty_print()

if __name__ == "__main__":
  manager = ToolsLlms()
  inputs = {"messages": [("user", "Add 34 + 21.")]}
  manager.print_stream(manager.agent.stream(inputs, stream_mode="values") )
