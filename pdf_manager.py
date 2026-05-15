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

  def get_chroma_data(self):
    # Load the existing database
    # Note: Use the same embedding function used when creating the DB
    vector_db = self.get_vector_store()

    # Retrieve all documents and their associated metadata
    # include=["documents", "metadatas"] ensures we get the text and file info
    collection = vector_db._client.get_collection(name=self.collection_name)
    results = collection.get(include=["documents"])

    data = []
    if results and 'documents' in results:
        for doc_id, doc_text in zip(results['ids'], results['documents']):
          data.append({'id': doc_id, 'text': doc_text})
    return data

  def get_vector_by_ids(self, ids):
    vector_store = self.get_vector_store()

    # Perform a similarity search to get matching Document objects
    # You can also use vector_store.get(ids=["id1"]) if you have specific IDs
    # results = vector_store.similarity_search(query, k=3)
    results = vector_store.get(ids=ids)
    view_data = []
    if results and results.get("documents"):
      text = results["documents"][0]
      metadata = results["metadatas"][0]

      view_data.append({
        "id": id,
        "text": text,  # Directly accessing the text from the dict
        "source": metadata.get("source", "Unknown")
      })

    return view_data

  def update_data_by_id(self, id):
    flash(f"Be here soon..", "info")
    return True

  def delete_pdf_by_source(vector_store, source_name):
    """
    Deletes all document chunks from Chroma that match a specific source name.
    """
    # 1. Fetch all document IDs associated with the specific source
    # Most LangChain loaders use 'source' as the default metadata key for filenames
    results = vector_store.get(where={"source": source_name})
    ids_to_delete = results.get('ids')

    if ids_to_delete:
        # 2. Delete the retrieved IDs from the vector store
        vector_store.delete(ids=ids_to_delete)
        print(f"Deleted {len(ids_to_delete)} chunks for source: {source_name}")
    else:
        print(f"No documents found for source: {source_name}")

  def delete_vector_by_id(self, ids: list[str]):
    vector_store = self.get_vector_store()
    try:
      vector_store.delete(ids=ids)
      flash(f"Successfully deleted IDs: {ids}", "success")
      return True
    except Exception as e:
      flash(f"Error deleting vectors: {e}", "danger")
      return False

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

