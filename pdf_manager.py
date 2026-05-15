import os
import uuid
import re
import unicodedata
from flask import flash
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader, TextLoader, DirectoryLoader, PythonLoader, UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

class PdfManager():
  def __init__(self):
    self.persist_directory = os.path.join(os.path.abspath("."), "database\\chroma_db")
    self.collection_name = 'missing_persons'
    self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

  def get_vector_store(self):
    # Initialize the vector store
    return Chroma(
      persist_directory=self.persist_directory,
      collection_name=self.collection_name,
      embedding_function=self.embeddings
    )

  def save(self, processor, filename):
    loader = PyPDFLoader(os.path.join(os.path.abspath("."), 'assets/files/', filename))
    pages = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=500,
      chunk_overlap=50
    )
    chunks = text_splitter.split_documents(pages)

    # 4. Create deterministic composite string IDs
    # Format: path_to_file_page_index_chunk_index
    ids = []
    chunk_counts = {}

    for idx, chunk in enumerate(chunks):
      # Extract source path and page number from metadata (note: page is 0-indexed)
      source = chunk.metadata.get("source", "unknown_source")
      page = chunk.metadata.get("page", 0)

      # Track chunk occurrences per page to ensure uniqueness
      page_key = (source, page)
      chunk_counts[page_key] = chunk_counts.get(page_key, 0) + 1
      chunk_num = chunk_counts[page_key]

      # Create composite ID
      composite_id = f"{os.path.basename(source)}_page{page}_chunk{chunk_num}"
      ids.append(composite_id)

      # Optionally attach this ID to the document metadata
      chunk.metadata["custom_id"] = composite_id
      chunk.metadata["source"] = os.path.basename(filename)
      chunk.metadata["chunk_index"] = idx

    embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": processor})
    Chroma.from_documents(
      documents=chunks,
      embedding=embedding_function,
      ids=ids,
      collection_name=self.collection_name,
      persist_directory=self.persist_directory
    )
    flash(f"Collection missing_persons saved {os.path.basename(filename)} successfully!", "success")
    return True

  def get_collection(self, filename):
    # get vector store
    vector_store = self.get_vector_store()

    # Get documents specifically from 'example.txt'
    docs = vector_store.get(
      where={"source": filename}
    )

    print(docs['documents'])

  def clean_filename(self, filename):
    # 1. Convert accented characters to ASCII equivalents (e.g., 'é' -> 'e')
    filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')

    # 2. Keep only alphanumeric characters, underscores, hyphens, and dots
    # This strips dangerous symbols like /, \, :, *, ?, ", <, >, |
    filename = re.sub(r'[^\w\s.-]', '', filename).strip()

    # 3. Replace internal spaces or multiple separators with a single underscore
    filename = re.sub(r'[-\s]+', '_', filename)

    # 4. Remove leading dots to prevent hidden files or directory traversal
    filename = filename.lstrip('.')

    return filename or "default_filename"

