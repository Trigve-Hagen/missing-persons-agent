# https://www.youtube.com/watch?v=jGg_1h0qzaM&t=2006s
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

class DocumentLlm:
  def __init__(self):
    self.tools = self.get_tools()

    self.llm = ChatOllama(
      model="qwen3.5:latest",
      temperature=0.1,
      num_ctx=2048
    ).bind_tools(tools=self.tools)

    self.conversation_history = []

    self.document_content = ""

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
    def update(content: str) -> str:
      """ Updates the document with the provided content. """
      self.document_content = content
      return f"Ducument has been updated. The current content is {self.document_content}"

    @tool
    def save(filename: str) -> str:
      """ Save the current document to a text file and finish the process.

      Args:
        filename: Name for the text file.
      """
      if not filename.endswith(".txt"):
        filename = f"{filename}.txt"

      try:
        with open(filename, 'w') as file:
          file.write(self.document_content)
        print(f"Document has beed saved to {filename}")
        return f"Document has beed saved to '{filename}'."
      except Exception as e:
        return f"Error saving document {str(e)}."

    return [update, save]

  def our_agent(self, state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content=f"""
    You are Drafter, a helpful writing assistant. You are going to help the user update and modify documents.

    - If the user wants to update or modify content, use the 'update' tool with the complete updated content.
    - If the user wants to save and finish, you need to use the 'save' tool.
    - Make sure to always show the current document state after modifications.

    The current document content is: {self.document_content}
    """)

    if not state["messages"]:
      user_input = "I'm ready to help you update a document. What would you like to create?"
      user_message = HumanMessage(content=user_input)
    else:
      user_input = "\nWhat would you like to do with the document?"
      print(f"USER: {user_input}")
      user_message = HumanMessage(content=user_input)

    all_messages = [system_prompt] + list(state["messages"]) + [user_message]

    response = self.llm.invoke(all_messages)

    print(f"\nAI: {response.content}")
    if hasattr(response, "tool_calls") and response.tool_calls:
      print(f"USING TOOLS: {[tc['name'] for tc in response.tool_calls]}")

    return {"messages": list(state["messages"]) + [user_message, response]}

  def should_continue(self, state: AgentState):
    """ Determine if we should continue or end the conversation. """
    messages = state["messages"]

    if not messages:
      return "continue"

    for message in reversed(messages):
      if (isinstance(message, ToolMessage) and
          "saved" in message.content.lower() and
          "document" in message.content.lower()):
        return "end"
    return "continue"

  def print_messages(self, messages):
    """ Print messages. """
    if not messages:
      return

    for message in messages[-3:]:
      if isinstance(message, ToolMessage):
        print(f"TOOL RESULT: {message.content}")

  def build_graph(self):
    graph = StateGraph(AgentState)
    graph.add_node("agent", self.our_agent)

    tool_node = ToolNode(tools=self.tools)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")

    graph.add_edge("agent", "tools")

    graph.add_conditional_edges(
      "tools",
      self.should_continue,
      {
        "continue": "agent",
        "end": END
      },
    )

    return graph.compile()

  def run_document_agent(self):
    print("\n ===== DRAFTER =====")

    state = {"messages": []}

    for step in self.agent.stream(state, stream_mode="values"):
      if "messages" in step:
        self.print_messages(step["messages"])

    print("\n ===== DRAFTER FINISHED =====")

if __name__ == "__main__":
  manager = DocumentLlm()
  manager.run_document_agent()
