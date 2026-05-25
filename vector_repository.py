import os
import re
import time
import sys
import unicodedata
from flask import flash
from database.state import State
from database.person import Person, Event, Note
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_docling.loader import DoclingLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Base class (Parent)
class VectorDb:
  def __init__(self, session):
    self.persist_directory = self.resource_path("database\\investigation_db")
    self.collection_name = 'missing_persons'
    state = session.get(State, 1)
    self.processor = state.processor
    self.chunk_size = state.chunk_size
    self.chunk_overlap = state.chunk_overlap
    self.embedding_function = self.get_embeddings()
    # self.directory = self.resource_path(f"database\\{state.database}")

  def resource_path(self, relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

  def get_vector_store(self):
    return Chroma(
      persist_directory=self.persist_directory,
      collection_name=self.collection_name,
      embedding_function=self.embedding_function
    )

  def load_pages(self, filename):
    loader = DoclingLoader(file_path=os.path.join(os.path.abspath("."), 'assets\\files\\', filename))

    pages = loader.load()
    return filter_complex_metadata(pages)

  def get_text_splitter(self, pages):
    text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=self.chunk_size,
      chunk_overlap=self.chunk_overlap,
      separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter.split_documents(pages)

  def get_embeddings(self):
    # flash(f"Processor: {self.processor}", "info")
    if not self.processor or self.processor == "None":
      embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    else:
      embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", model_kwargs={"device": self.processor})

    return embedding_function

  def get_all_chroma_data(self):
    vector_store = Chroma(
      persist_directory=self.persist_directory,
      collection_name=self.collection_name,
      embedding_function=self.embedding_function
    )

    collection = vector_store._client.get_collection(name=self.collection_name)
    # Retrieve records matching both param1 AND param2
    results = collection.get(
      include=["documents", "metadatas"],
    )
    metadatas = results["metadatas"]

    data = []
    if results and 'documents' in results:
      for doc_id, doc_text, doc_metas in zip(results['ids'], results['documents'], results['metadatas']):
        data.append({'id': doc_id, 'text': doc_text, 'meta': doc_metas})
    return data, metadatas

  def get_chroma_data(self, type, id):
    vector_store = self.get_vector_store()
    try:
      collection = vector_store._client.get_collection(name=self.collection_name)
      # Retrieve records matching both param1 AND param2
      where = {}
      if type != "" and type != 'None':
        where = {
          "$and": [
              {"vector_type": type},
              {"entity_id": id}
          ]
        }

      results = collection.get(
        include=["documents", "metadatas"],
        where=where
      )
      metadatas = results["metadatas"]

      data = []
      if results and 'documents' in results:
        for doc_id, doc_text, doc_metas in zip(results['ids'], results['documents'], results['metadatas']):
          data.append({'id': doc_id, 'text': doc_text, 'meta': doc_metas})
      return data, metadatas
    except Exception as e:
      flash(f"Error retrieving data: {e}", "danger")
      return [], []

  def get_vector_by_ids(self, ids):
    vector_store = self.get_vector_store()
    try:
      results = vector_store.get(ids=ids)
      view_data = []
      if results and results.get("documents"):
        text = results["documents"][0]
        metadata = results["metadatas"][0]

        view_data.append({
          "id": id,
          "text": text,
          "meta": metadata,
          "source": metadata.get("source", "Unknown")
        })

      return view_data
    except Exception as e:
      flash(f"Error retrieving data: {e}", "danger")
      return []

  def update_data_by_id(self, vector_id: str, content: str, metadata: dict):
    vector_store = self.get_vector_store()
    try:
      collection = vector_store._collection
      collection.upsert(
          ids=[vector_id],
          documents=[content],
          metadatas=[metadata],
      )
      flash(f"Successfully updated {vector_id}!", "success")
      return True
    except ValueError as ve:
      flash(f"Document ID not found or invalid payload: {ve}", "danger")
    except Exception as e:
      flash(f"Error deleting vectors: {e}", "danger")
      return False

  def delete_vector_by_id(self, ids: list[str]):
    vector_store = self.get_vector_store()
    try:
      vector_store.delete(ids=ids)
      flash(f"Successfully deleted IDs: {ids}", "success")
      return True
    except Exception as e:
      flash(f"Error deleting vectors: {e}", "danger")
      return False

  def delete_file_by_source(self, source):
    vector_store = self.get_vector_store()
    try:
      collection = vector_store._client.get_collection(name=self.collection_name)
      collection.delete(
          where={"source": source}
      )
      flash(f"Successfully deleted File: {source}", "success")
      return True
    except Exception as e:
      flash(f"Error deleting file: {e}", "danger")
      return False

  def machine_name(self, filename):
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

  def save_doc(self, pages, type, name, record):
    chunks = self.get_text_splitter(pages)
    # 4. Create deterministic composite string IDs
    # Format: path_to_file_page_index_chunk_index
    ids = []
    chunk_counts = {}

    for idx, chunk in enumerate(chunks):
      # Extract source path and page number from metadata (note: page is 0-indexed)
      source = chunk.metadata.get("source", "unknown_source")
      page = chunk.metadata.get("page", 1)

      # Track chunk occurrences per page to ensure uniqueness
      page_key = (source, page)
      chunk_counts[page_key] = chunk_counts.get(page_key, 0) + 1
      chunk_num = chunk_counts[page_key]

      # Create composite ID
      composite_id = f"{os.path.basename(source)}_page{page}_chunk{chunk_num}"
      ids.append(composite_id)

      # Optionally attach this ID to the document metadata
      chunk.metadata["vector_type"] = "file"
      chunk.metadata["custom_id"] = composite_id
      chunk.metadata["owner"] = record.owner
      chunk.metadata["entity_id"] = record.id

      if type == 'file':
        chunk.metadata["source"] = os.path.basename(name)
      else:
        chunk.metadata["source"] = self.machine_name(name)

      chunk.metadata["chunk_index"] = (idx + 1)


    Chroma.from_documents(
      documents=chunks,
      embedding=self.embedding_function,
      ids=ids,
      collection_name=self.collection_name,
      persist_directory=self.persist_directory
    )

class PdfRepository(VectorDb):

  def save_document(self, record, filename):
    pages = self.load_pages(filename)
    self.save_doc(pages, 'file', filename, record)

    flash(f"Collection missing_persons saved {os.path.basename(filename)} successfully!", "success")
    return True

class PersonRepository(VectorDb):

  def save_person(self, person):
    person_content = repr(person)

    s1, s2, s3, s4, s5 = person.sirName, person.firstName, person.middleName, person.lastName, person.suffix
    name = " ".join([s for s in [s1, s2, s3, s4, s5] if s])

    ids = []

    # Create composite ID
    composite_id = f"{self.machine_name(name)}_{time.time_ns()}_chunk1"
    ids.append(composite_id)

    document = Document(
      page_content=person_content,
      metadata={
        "vector_type": "person",
        "chunk_index": 1,
        "custom_id": composite_id,
        "source": f"{self.machine_name(name)}_{time.time_ns()}",
        "entity_id": person.id
      }
    )

    chunks = self.get_text_splitter([document])

    Chroma.from_documents(
      documents=chunks,
      embedding=self.embedding_function,
      ids=ids,
      collection_name=self.collection_name,
      persist_directory=self.persist_directory
    )

    flash(f"{person_content} saved successfully!", "success")
    return True

class EventRepository(VectorDb):

  def save_event(self, event):
    event_content = repr(event)

    ids = []

    # Create composite ID
    composite_id = f"{self.machine_name(event.name)}_{time.time_ns()}_chunk1"
    ids.append(composite_id)

    document = Document(
      page_content=event_content,
      metadata={
        "vector_type": "event",
        "chunk_index": 1,
        "custom_id": composite_id,
        "source": f"{self.machine_name(event.name)}_{time.time_ns()}",
        "entity_id": event.id
      }
    )

    chunks = self.get_text_splitter([document])

    Chroma.from_documents(
      documents=chunks,
      embedding=self.embedding_function,
      ids=ids,
      collection_name=self.collection_name,
      persist_directory=self.persist_directory
    )

    flash(f"{event_content} saved successfully!", "success")
    return True

class NoteRepository(VectorDb):

  def save_note(self, note):
    note_content = repr(note)

    ids = []

    # Create composite ID
    composite_id = f"{self.machine_name(note.name)}_{time.time_ns()}_chunk1"
    ids.append(composite_id)

    document = Document(
      page_content=note_content,
      metadata={
        "vector_type": "note",
        "chunk_index": 1,
        "custom_id": composite_id,
        "source": f"{self.machine_name(note.name)}_{time.time_ns()}",
        "entity_id": note.id
      }
    )

    chunks = self.get_text_splitter([document])

    Chroma.from_documents(
      documents=chunks,
      embedding=self.embedding_function,
      ids=ids,
      collection_name=self.collection_name,
      persist_directory=self.persist_directory
    )

    flash(f"{note_content} saved successfully!", "success")
    return True

class JsonRepository(VectorDb):

  def save_json(self, note):
    note_content = repr(note)

    ids = []

    # Create composite ID
    composite_id = f"{self.machine_name(note.name)}_{time.time_ns()}_chunk1"
    ids.append(composite_id)

    document = Document(
      page_content=note_content,
      metadata={
        "vector_type": "json",
        "chunk_index": 1,
        "custom_id": composite_id,
        "source": f"{self.machine_name(note.name)}_{time.time_ns()}",
        "entity_id": note.id
      }
    )

    chunks = self.get_text_splitter([document])

    Chroma.from_documents(
      documents=chunks,
      embedding=self.embedding_function,
      ids=ids,
      collection_name=self.collection_name,
      persist_directory=self.persist_directory
    )

    flash(f"{note_content} saved successfully!", "success")
    return True

