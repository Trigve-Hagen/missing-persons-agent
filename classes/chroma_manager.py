import os
import time
from flask import flash
from langchain_chroma import Chroma
from langchain_core.documents import Document
from classes.chroma_database import ChromaDatabase
from classes.model_utils import ModelUtils

class PdfRepository(ChromaDatabase):

  def save_document(self, record, filename):
    pages = self.load_pages(filename)
    self.save_doc(pages, 'file', filename, record)

    flash(f"Collection missing_persons saved {os.path.basename(filename)} successfully!", "success")
    return True

class PersonRepository(ChromaDatabase):

  def save_person(self, person):
    person_content = repr(person)

    s1, s2, s3, s4, s5 = person.sirName, person.firstName, person.middleName, person.lastName, person.suffix
    name = " ".join([s for s in [s1, s2, s3, s4, s5] if s])

    ids = []

    # Create composite ID
    composite_id = f"{ModelUtils.machine_name(name=name)}_{time.time_ns()}_chunk1"
    ids.append(composite_id)

    document = Document(
      page_content=person_content,
      metadata={
        "vector_type": "person",
        "chunk_index": 1,
        "custom_id": composite_id,
        "source": f"{ModelUtils.machine_name(name=name)}_{time.time_ns()}",
        "entity_id": person.id
      }
    )

    chunks = self.get_text_splitter([document])

    Chroma.from_documents(
      documents=chunks,
      embedding=self.embedding_function,
      ids=ids,
      collection_name=self.collection_name,
      persist_directory=self.investigation_db
    )

    flash(f"{person_content} saved successfully!", "success")
    return True

class EventRepository(ChromaDatabase):

  def save_event(self, event):
    event_content = repr(event)

    ids = []

    # Create composite ID
    composite_id = f"{ModelUtils.machine_name(name=event.name)}_{time.time_ns()}_chunk1"
    ids.append(composite_id)

    document = Document(
      page_content=event_content,
      metadata={
        "vector_type": "event",
        "chunk_index": 1,
        "custom_id": composite_id,
        "source": f"{ModelUtils.machine_name(name=event.name)}_{time.time_ns()}",
        "entity_id": event.id
      }
    )

    chunks = self.get_text_splitter([document])

    Chroma.from_documents(
      documents=chunks,
      embedding=self.embedding_function,
      ids=ids,
      collection_name=self.collection_name,
      persist_directory=self.investigation_db
    )

    flash(f"{event_content} saved successfully!", "success")
    return True

class ReportRepository(ChromaDatabase):

  def save_report(self, report):
    report_content = repr(report)

    ids = []

    # Create composite ID
    composite_id = f"{ModelUtils.machine_name(name=report.name)}_{time.time_ns()}_chunk1"
    ids.append(composite_id)

    document = Document(
      page_content=report_content,
      metadata={
        "vector_type": "report",
        "chunk_index": 1,
        "custom_id": composite_id,
        "source": f"{ModelUtils.machine_name(name=report.name)}_{time.time_ns()}",
        "entity_id": report.id
      }
    )

    chunks = self.get_text_splitter([document])

    Chroma.from_documents(
      documents=chunks,
      embedding=self.embedding_function,
      ids=ids,
      collection_name=self.collection_name,
      persist_directory=self.investigation_db
    )

    flash(f"{report_content} saved successfully!", "success")
    return True

class JsonRepository(ChromaDatabase):

  def save_json(self, report):
    report_content = repr(report)

    ids = []

    # Create composite ID
    composite_id = f"{ModelUtils.machine_name(name=report.name)}_{time.time_ns()}_chunk1"
    ids.append(composite_id)

    document = Document(
      page_content=report_content,
      metadata={
        "vector_type": "json",
        "chunk_index": 1,
        "custom_id": composite_id,
        "source": f"{ModelUtils.machine_name(name=report.name)}_{time.time_ns()}",
        "entity_id": report.id
      }
    )

    chunks = self.get_text_splitter([document])

    Chroma.from_documents(
      documents=chunks,
      embedding=self.embedding_function,
      ids=ids,
      collection_name=self.collection_name,
      persist_directory=self.investigation_db
    )

    flash(f"{report_content} saved successfully!", "success")
    return True

""" class Determinator(ChromaDatabase):
  Takes a list of sql create statements and saves them as vectors.

  def chunk_create_statements(self, createStatements):
    vector_store = Chroma(
      persist_directory=ModelUtils.resource_path(os.path.join("database", "determinator_db")),
      collection_name=self.collection_name,
      embedding_function=self.embedding_function
    )
    try:
      matching_docs = vector_store.get(
        limit=1,
        where={"source": {"$eq": "create_statements"}}
      )

      if not matching_docs["metadatas"]:
        ids = []
        documents = []
        for index, (title, sql_statement) in enumerate(createStatements.items()):
          entity = ModelUtils.machine_name(name=title)
          composite_id = f"create_statements_{entity}_chunk{index}"
          ids.append(composite_id)

          doc = Document(
              page_content=sql_statement,
              metadata={
                "vector_type": "create_statements",
                "chunk_index": index,
                "custom_id": composite_id,
                "source": f"create_statements",
                "entity": entity
              }
          )
          documents.append(doc)

        Chroma.from_documents(
          documents=documents,
          embedding=self.embedding_function,
          ids=ids,
          collection_name=self.collection_name,
          persist_directory=self.determinator_db
        )

        flash(f"Successfully saved {len(createStatements)} statements to Chroma at '{self.determinator_db}'.", "success")

    except Exception as e:
      flash(f"Error retrieving data: {e}", "danger")
      return [] """
