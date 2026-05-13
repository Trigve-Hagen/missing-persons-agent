# Break down each task that needs to be done when creating a RAG LLM.
  # Choose the best sentence tranformer from the list of free transformers @ https://huggingface.co
# Create models that handle each of these tasks.
  # What is the best approach?
import os
import uuid
from flask import flash
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader, TextLoader, DirectoryLoader, PythonLoader, UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
# Choose the best sentence tranformer from the list of free transformers @ https://huggingface.co
class PdfManager():
  def __init__(self, filename):
    self.filename = filename
    self.base_path = os.path.abspath(".")
    self.file_path = os.path.join(self.base_path, 'assets/files/', self.filename)
    self.database_path = os.path.join(self.base_path, "database/chroma_db")

  def save(self):
    loader = PyPDFLoader(self.file_path)
    pages = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=1000,
      chunk_overlap=100,
      add_start_index=True
    )
    chunks = text_splitter.split_documents(pages)

    for i, chunk in enumerate(chunks):
      chunk.metadata["id"] = str(uuid.uuid4())
      chunk.metadata["source"] = os.path.basename(self.filename)
      chunk.metadata["chunk_index"] = i

    embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})
    Chroma.from_documents(
      chunks,
      embedding_function,
      collection_name="missing_persons",
      persist_directory=self.database_path
    )
    flash(f"Collection missing_persons saved {os.path.basename(self.filename)} successfully!", "success")
    return True

  def get_collection(self):
    vectorstore = Chroma(
      persist_directory=self.database_path,
      embedding_function=HuggingFaceEmbeddings(),
      collection_name="missing_persons"
    )

    # Get documents specifically from 'example.txt'
    docs = vectorstore.get(
      where={"source": self.filename}
    )

    print(docs['documents'])

  def suggest_embedding():
    return 'all-MiniLM-L6-v2'

