import os
import re
import platform
import ollama
import json
import sys
from flask import flash
from sqlalchemy import select
from database.state import State
from database.model import Model, Prompt, Question
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from classes.model_utils import ModelUtils
from classes.chroma_database import ChromaDatabase
from datetime import datetime
from langchain_community.llms import Ollama
from langchain_core.output_parsers import JsonOutputParser

# ---------------------------------------------------------
# 1. Pydantic Schemas for Structured LLM Output
# ---------------------------------------------------------

class TaskSuggestion(BaseModel):
    title: str = Field(description="Short title of the task")
    description: str = Field(description="Detailed steps or context for the task")

class TaskList(BaseModel):
    suggestions: List[TaskSuggestion] = Field(description="List of exactly 10 task suggestions")

class Task(BaseModel):
    name: str = Field(..., description="The name of the task.")
    description: str = Field(..., description="A human-readable description of the data and action needed.")
    if_complete: int = Field(default=0, description="Default to 0.")
    dateCreated: datetime = Field(default_factory=datetime.now)
    dateCompleted: Optional[datetime] = Field(default=None)

class Statement(BaseModel):
    sql_table_name: str = Field(..., description="The name of the SQL table where the data fits best.")
    sql_insert_statement: str = Field(..., description="The exact raw SQL INSERT statement to execute.")

class ExtractionResult(BaseModel):
    task: Task
    statement: Statement

class ChatManager(ChromaDatabase):
  def inspector(self, model):
    if model:
      try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        if os.path.exists(self.persistent_directory):
            vectorstore = Chroma(
              persist_directory=self.persistent_directory,
              embedding_function=embeddings,
              collection_name=self.collection_name
            )
        else:
            flash(f"Chroma collection not found at {self.persistent_directory}", "danger")
            return False

        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        llm = ChatOllama(model=model.model)

        try:
          qa_chain = RetrievalQA.from_chain_type(
              llm=llm,
              chain_type="stuff",
              retriever=retriever,
              return_source_documents=False
          )
          return qa_chain
        except Exception as e:
          flash(f"Error fetching chain: {e}", "danger")
          return False
      except Exception as e:
        flash(f"Error prompting models: {e}", "danger")
        return False
    else:
      flash(f"Error fetching models: Please set a model.", "danger")
      return False

  def suggestions(self, model, prompt, question):
    if model:
      try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        if os.path.exists(self.persist_directory):
            vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=embeddings,
                collection_name=self.collection_name
            )
        else:
            flash(f"Chroma collection not found at {self.persist_directory}", "danger")
            return False

        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        llm = ChatOllama(model=model.model, format="json", temperature=0.7)

        parser = PydanticOutputParser(pydantic_object=TaskList)
        chat_prompt_template = ChatPromptTemplate.from_template(
          "{prompt}\n"
          "Context: {context}\n"
          "User Request: {query}\n"
          "{format_instructions}"
        )

        try:
          context_docs = retriever.invoke(question.question)
          context_text = "\n".join([doc.page_content for doc in context_docs])
          chain = chat_prompt_template | llm | parser
          response = chain.invoke({
            "prompt": prompt.prompt,
            "context": context_text,
            "query": question.question,
            "format_instructions": parser.get_format_instructions()
          })
          return response
        except Exception as e:
          flash(f"Error fetching chain: {e}", "danger")
          return False
      except Exception as e:
        flash(f"Error prompting models: {e}", "danger")
        return False
    else:
      flash(f"Error fetching models: Please set a model.", "danger")
      return False

  def determine(self, json_payload: str, db_schemas: str) -> ExtractionResult:
    """ Takes a json response object and parses it into useable data that
    can be inserted into the sql_alchemy database. It creates Tasks that
    explains in human readable format what it is doing with the statement.
    It also inserts a row in statement that is the table name and insert
    statement to insert the data into the database.
    """

    # Assumes Ollama is running locally and you have a model like 'llama3' or 'mistral'
    llm = Ollama(model="llama3")

    system_prompt = """
    You are an AI research agent analyzing missing person data feeds (JSON).
    Your job is to identify relevant data, create a human-readable task for logging,
    and formulate a safe, ready-to-execute SQL INSERT statement.

    You have access to the following Database context (Schema chunks):
    {db_schemas}

    When given an input JSON, you must:
    1. Extract data points related to the missing person.
    2. Formulate a 'task' (name and description) to document this data.
    3. Generate a SQL INSERT statement targeting the most appropriate table (from your schema context).
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Here are the database schema chunks to guide you:\n{db_schemas}\n\nHere is the API/RSS JSON data to process:\n{json_data}")
    ])

    # Set up parser with Pydantic schema
    parser = JsonOutputParser(pydantic_object=ExtractionResult)

    # Format the chain
    chain = prompt | llm | parser

    # Invoke the model with inputs
    result = chain.invoke({
        "db_schemas": db_schemas,
        "json_data": json_payload
    })
