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
from typing import List, Optional
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
from typing_extensions import TypedDict
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

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

class ExtractionResult(BaseModel):
    task: Task

# ---------------------------------------------------------
# State
# ---------------------------------------------------------

class AgentState(TypedDict):
  messages: List[HumanMessage]

# ---------------------------------------------------------
# LLMs
# ---------------------------------------------------------

class PracticeLlms(ChromaDatabase):
  def __init__(self, session, model):
    # 1. Pass the required argument up to the parent class
    super().__init__(session=session)

    self.llm = ChatOllama(
      model=model.model,
      temperature=model.temperature,
      num_ctx=model.num_ctx
    )

    self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    self.vector_store = Chroma(
      persist_directory=self.persistent_directory,
      embedding_function=self.embeddings,
      collection_name=self.collection_name
    )
    self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

    self.agent = self.build_graph()

  def process(self, state: StateGraph) -> AgentState:
    response = self.llm.invoke(state['messages'])
    print(f"AI: {response.content}")
    return state

  def build_graph(self):
    graph = StateGraph(AgentState)
    graph.add_node("process", self.process)
    graph.add_edge(START, "process")
    graph.add_edge("process", END)

    return graph.compile()

  def invoke(self, user_input: str):
    return self.agent.invoke({"messages": [HumanMessage(content=user_input)]})

