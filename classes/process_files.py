import os
import shutil
from flask import flash
from database.state import State
from langchain_community.document_loaders import PythonLoader
from langchain_text_splitters import PythonCodeTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

class ProcessFiles():
  def __init__(self, session):
    self.base_path = os.path.abspath(".")
    self.state_py = os.path.join(self.base_path, "database", "state.py")
    self.code_optimize_directory = os.path.join(self.base_path, "database\\code_optimize_db")
    self.collection_name = "missing_persons"
    state = session.get(State, 1)
    self.processor = state.processor
    self.chunk_size = state.chunk_size
    self.chunk_overlap = state.chunk_overlap

  def delete_code_chroma(self):
    if os.path.exists(self.code_optimize_directory):
        try:
            shutil.rmtree(self.code_optimize_directory)
            flash(f"{self.code_optimize_directory} removed successfully!", "success")
        except Exception as e:
            flash(f"Error deleting {self.code_optimize_directory}: {e}", "danger")
            return False

  def process_and_save_code(self):
    python_splitter = PythonCodeTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )

    documents = []
    """ for root, _, files in os.walk(self.base_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file) """
    try:
        loader = PythonLoader(self.state_py)
        documents.extend(loader.load())
    except Exception as e:
        flash(f"Error loading {self.state_py}: {e}", "info")

    chunks = python_splitter.split_documents(documents)
    embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": self.processor})

    flash("Saving to Chroma vector store...", "info")
    Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        collection_name=self.collection_name,
        persist_directory=self.code_optimize_directory
    )

    flash(f"Successfully saved chunks to Chroma collection: {self.collection_name}")
