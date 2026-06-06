import os
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
from langchain_core.output_parsers import PydanticOutputParser
from langchain_classic.chains import create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from classes.model_utils import ModelUtils
from classes.chroma_database import ChromaDatabase
from datetime import datetime
from langchain_core.tools import tool

# LangGraph imports
from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

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

# ---------------------------------------------------------
# LLangGraph State and Workflow Nodes
# ---------------------------------------------------------

class ChatState(TypedDict):
    input: str
    chat_history: Annotated[Sequence, add_messages]
    context: str
    answer: str

# ---------------------------------------------------------
# LLMs
# ---------------------------------------------------------

class ChatManager(ChromaDatabase):
  def __init__(self, session, model):
    # 1. Pass the required argument up to the parent class
    super().__init__(session=session)

    if model:
      self.llm = ChatOllama(
        model=model.model,
        temperature=model.temperature,
        num_ctx=model.num_ctx
      )

      self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
      if os.path.exists(self.persistent_directory):
        self.vector_store = Chroma(
          persist_directory=self.persistent_directory,
          embedding_function=self.embeddings,
          collection_name=self.collection_name
        )
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
      else:
        flash(f"Chroma collection not found at {self.persistent_directory}", "danger")
        return False
    else:
      flash(f"Error fetching models: Please set a model.", "danger")
      return False

    # Compile components & graph
    self._init_chains()
    self.graph = self._build_graph()

  def _init_chains(self):
    # Query rewriting chain
    retriever_history_prompt = ChatPromptTemplate.from_messages([
      MessagesPlaceholder(variable_name="chat_history"),
      ("human", "{input}"),
      ("human", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
    ])
    self.history_aware_retriever = create_history_aware_retriever(
      self.llm, self.retriever, retriever_history_prompt
    )

    # Document synthesis chain
    qa_prompt = ChatPromptTemplate.from_messages([
      ("system", "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, say that you don't know.\n\nContext:\n{context}"),
      MessagesPlaceholder(variable_name="chat_history"),
      ("human", "{input}"),
    ])
    self.question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)

  def _graph_node(self, state: ChatState):
    # Step A: Fetch relative documentation
    docs = self.history_aware_retriever.invoke({
      "input": state["input"],
      "chat_history": state["chat_history"]
    })

    # Step B: Generate final answer
    response_text = self.question_answer_chain.invoke({
      "input": state["input"],
      "chat_history": state["chat_history"],
      "context": docs
    })

    return {
      "context": docs,
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

    # Keep track of history via MemorySaver
    return workflow.compile(checkpointer=MemorySaver())

  def chat_prompt(self, user_message: str, session_id: str):
    """Executes the state graph loop for a unique thread session."""
    config = {"configurable": {"thread_id": session_id}}

    output = self.graph.invoke(
      {"input": user_message},
      config=config
    )

    return output["answer"]

  def suggestions(self, model: Model, prompt: Prompt, question: Question):
    if model:
      try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        if os.path.exists(self.investigation_db):
            vector_store = Chroma(
              persist_directory=self.investigation_db,
              embedding_function=embeddings,
              collection_name=self.collection_name
            )
        else:
            flash(f"Chroma collection not found at {self.investigation_db}", "danger")
            return False

        retriever = vector_store.as_retriever(search_kwargs={"k": 5})
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

  def determine(self, person: Person, model: Model, json_payload: str) -> ExtractionResult:
    """ Takes a json response object and parses it into useable data that
    can be inserted into the sql_alchemy database. It creates Tasks that
    explains in human readable format what it is doing with the statement.
    It also inserts a row in statement that is the table name and insert
    statement to insert the data into the database.
    """

    # Get the database schema.
    try:
      determinator_db = ModelUtils.resource_path(os.path.join("database", "determinator_db"))
      if os.path.exists(determinator_db):
        results = self.get_collection("determinator_db")
        db_schemas = "\n\n".join(results.get("documents", []))
        flash(f"Chroma collection: {db_schemas}", "success")
      else:
        flash(f"Chroma collection not found at {determinator_db}", "danger")
        return False
    except Exception as e:
        flash(f"Error getting database schema: {e}", "danger")
        return False

    # Get the missing person to filter out unrelated data.
    missing_person = repr(person)

    # Initialize the Ollama LLM (Ensure the model, like llama3, is pulled locally)
    llm = ChatOllama(
      model=model.model,
      temperature=model.temperature,
      num_ctx=model.num_ctx
    )

    # Bind the Pydantic schema to force structured JSON output from the model
    structured_llm = llm.with_structured_output(ExtractionResult)

    # Create the prompt template with strict instructions
    prompt = ChatPromptTemplate.from_messages([
      ("system", (
        "You are an expert data engineering agent for a missing persons investigation platform.\n\n"
        "Your job is to analyze incoming JSON data from external feeds and map it to the best available "
        "database table based on the provided database schema context, avoiding duplicates.\n\n"
        "You must output two things inside the structured schema:\n"
        "1. Task Tracking: A human-readable name and description for the 'tasks' table to log this action.\n"
        "2. SQL Generation: The target table name and a fully formed, valid SQL INSERT statement "
        "ready for execution.\n\n"
        "CRITICAL SQL RULES:\n"
        "- Do not include the 'owner' column or 'id' column in the INSERT statement. The backend handling script "
        "will automatically inject the generated task foreign key ID and primary keys.\n"
        "- Escape text quotes properly to avoid SQL syntax errors.\n"
        "- Only map to tables explicitly mentioned or implied by the database context."
        "- Only map data related to the missing person."
        "- Do not map data if it is already saved to the database."
      )),
      ("user", (
        "DATABASE SCHEMA CONTEXT:\n{schema_context}\n\n"
        "INCOMING JSON DATA:\n{json_data}\n\n"
        "MISSING PERSON:\n{missing_person}\n\n"
        "Analyze the data and generate the structured task and SQL insert statement."
      ))
    ])

    # Combine the prompt template with the structured LLM execution chain
    chain = prompt | structured_llm

    try:
      # Run the chain
      return chain.invoke({
        "schema_context": db_schemas,
        "json_data": json_payload,
        "missing_person": missing_person
      })
    except Exception as e:
        flash(f"Error invoking the chain: {e}", "danger")
        return False
