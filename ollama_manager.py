import os
import re
import platform
import ollama
from flask import flash
from sqlalchemy import create_engine, inspect, exc, select, update
from database.state import State
from database.model import Model
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_classic.chains.retrieval_qa.base import RetrievalQA

class OllamaManager:
  def __init__(self, session):
    self.session = session
    self.client = ollama.Client()
    self.base_path = os.path.abspath(".")
    self.persistent_directory = os.path.join(self.base_path, "database/chroma_db")
    self.collection_name = "missing_persons"
    self.model_name = "phi3:mini"

  def initialize():
    pass

  def prompt(self):
    state = self.session.execute(select(State).filter_by(id = 1)).scalar_one_or_none()
    model = self.session.execute(select(Model).filter_by(id = state.model)).scalar_one_or_none()

    if model:
      try:
        # --- Initialize LangChain Components ---
        # Load HuggingFace Embeddings
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        # Load existing Chroma collection
        if os.path.exists(self.persistent_directory):
            vectorstore = Chroma(
                persist_directory=self.persistent_directory,
                embedding_function=embeddings,
                collection_name=self.collection_name
            )
        else:
            # raise ValueError(f"Chroma collection not found at {self.persistent_directory}")
            flash(f"Chroma collection not found at {self.persistent_directory}", "danger")
            return False

        # Initialize Ollama model
        llm = ChatOllama(model=model.model)

        # Create Retriever
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        try:
          # Create Chain
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

  def suggestions(self):
    model = "deepseek-coder-v2"

    if model:
      try:
        # --- Initialize LangChain Components ---
        # Load HuggingFace Embeddings
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        # Load existing Chroma collection
        if os.path.exists(self.persistent_directory):
            vectorstore = Chroma(
                persist_directory=self.persistent_directory,
                embedding_function=embeddings,
                collection_name=self.collection_name
            )
        else:
            # raise ValueError(f"Chroma collection not found at {self.persistent_directory}")
            flash(f"Chroma collection not found at {self.persistent_directory}", "danger")
            return False

        # Initialize Ollama model
        llm = ChatOllama(model=model.model)

        # Create Retriever
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        try:
          # Create Chain
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

  def get_models(self):
    """Lists all locally downloaded models."""
    models = []
    try:
      models = self.client.list()
    except Exception as e:
      flash(f"Error fetching models: {e}", "danger")

    return models

  def is_model_downloaded(self, name):
    # checks if the model is downloaded already.
    local_models = ollama.list()
    for model in local_models['models']:
      if model['model'] == name:
        return True
    return False

  def download_model(self, model_name: str):
    # Downloads/Pulls an Ollama model.
    try:
      ollama.pull(model_name)
      flash(f"Model {model_name} downloaded successfully.", "success")
      return True
    except ollama.ResponseError as e:
      if "404" in str(e):
        flash(f"Model '{model_name}' does not exist on ollama.com.", "danger")
      else:
        flash(f"An error occurred: {e}", "danger")
      return False
    except Exception as e:
      flash(f"Error fetching models: {e}", "danger")
      return False

  def create_machine_name(self, text):
    text = text.lower()
    text = re.sub(r'[\s\-]+', '_', text)
    text = re.sub(r'[^\w]', '', text)
    return text.strip('_')

  def create_model(self, model: Model, parameters):
    try:
      ollama.create(
          model=self.create_machine_name(model.name),
          from_=model.model,
          system=model.system,
          parameters=parameters
      )
      flash(f"Model {model.name} created successfully.", "success")
      return True
    except Exception as e:
      flash(f"Error creating model: {e}", "danger")
      return False

  def stop_model(self, model_name: str):
    """Stops/Unloads a model from memory."""
    print(f"Stopping {model_name}...")
    # Setting keep_alive=0 purges the model from memory
    self.client.generate(model_name, keep_alive=0)
    print(f"Model {model_name} stopped.")

  def remove_model(self, model_name: str):
    """Removes a model from the system."""
    try:
      self.client.delete(model_name)
      flash(f"Model {model_name} removed.", "success")
      return True
    except Exception as e:
      flash(f"Error removing model: {e}", "danger")
      return False

  def get_ollama_storage_gb(self):
    """ Returns the total size of Ollama's model storage in Gigabytes. """
    # Determine default path based on OS
    home = os.path.expanduser("~")
    system = platform.system()

    if system == "Windows":
      path = os.path.join(home, ".ollama", "models")
    elif system == "Darwin":  # macOS
      path = os.path.join(home, ".ollama", "models")
    else:  # Linux (standard default)
      path = "/usr/share/ollama/.ollama/models"
      if not os.path.exists(path):
        path = os.path.join(home, ".ollama", "models")

    # If the user has set a custom path via OLLAMA_MODELS, use that instead
    path = os.environ.get("OLLAMA_MODELS", path)

    if not os.path.exists(path):
      return 0.0

    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
      for f in filenames:
        fp = os.path.join(dirpath, f)
        # skip if it is a symbolic link
        if not os.path.islink(fp):
          total_size += os.path.getsize(fp)

    # Convert bytes to Gigabytes
    return total_size / (1024**3)

# --- Usage Example ---
# manager = OllamaManager()

# Example workflow
# manager.download_model("llama3")
# manager.list_models()
# manager.stop_model("llama3")
# manager.remove_model("llama3")
# manager.get_ollama_storage_gb()
