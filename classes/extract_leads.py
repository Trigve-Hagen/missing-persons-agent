import os
import json
import ollama
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
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder,  PromptTemplate
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

class MissingPersonsLead(BaseModel):
  full_name: Optional[str] = Field(None, description="The full name of the lead.")
  relationship_to_subject: Optional[str] = Field(
    None, description="How this person relates to the missing individual (e.g., witness, family, last seen with, person of interest, suspect or associate)."
  )
  email: Optional[str] = Field(None, description="The email address if available.")
  phone: Optional[str] = Field(None, description="The phone number if available.")
  date_of_birth: Optional[str] = Field(None, description="The date of birth if available.")
  context: str = Field(description="Context, notes, or details about the lead.")


# ---------------------------------------------------------
# State
# ---------------------------------------------------------

class AgentState(TypedDict):
  messages: Annotated[Sequence[BaseMessage], add_messages]

# ---------------------------------------------------------
# LLMs
# ---------------------------------------------------------

class ExtractLeads(ChromaDatabase):
  def __init__(self, session, model):
    super().__init__(session=session)

    self.llm = ChatOllama(
      model=model.model,
      temperature=model.temperature,
      num_ctx=model.num_ctx
    )

    self.model=model.model


  # 2. Free, offline extraction function using Ollama
  def run_agent(self, name: str, raw_payload_text: str) -> MissingPersonsLead:
    system_prompt = (
      "Act as an expert intelligence analyst specializing in missing persons investigations. "
      "Your task is to analyze the text and extract leads. "
      f"Focus strictly on leads involving the target person {name}. "
      "Extract leads defined by keywords like witness, family, last seen with, person of interest, suspect or associate. "
      "Extract the context of the lead defining ther relationship to the target person. "
      "Populate the requested JSON schema fields using facts directly from the text. "
      "Do not assume facts. If the target person is not found, return an empty leads array."
    )

    user_prompt = (
      f"Extract the lead information from the following text:\n{raw_payload_text}"
    )

    # Fire request to your local engine
    response = ollama.chat(
      model=self.model,
      messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
      ],
      # Forces the local Qwen model to conform exactly to your Pydantic schema
      format=MissingPersonsLead.model_json_schema()
    )

    # 3. Parse the raw string response back into your Pydantic object
    return response['message']['content']
    # return LeadExtractionContainer.model_validate_json(response_text)

  def extract_leeds(self, person: str, data: str):
    try:
      # Run the local agent
      return self.run_agent(person, data)
    except Exception as e:
      flash(f"Execution Error: {e}", "danger")
      flash(f"Ensure Ollama is actively running in your background menu bar!", "info")
