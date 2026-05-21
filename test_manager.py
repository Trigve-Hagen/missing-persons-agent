from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

class TestManager():
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

  def list_chunks(self):
    # Load the existing database
    vector_store = self.get_vector_store()

    # Fetch all records from the collection
    # .get() returns a dictionary containing 'ids', 'metadatas', and 'documents'

    data = vector_store.get()

    print(f"--- Records in '{self.collection_name}' ---")
    for i in range(len(data['ids'])):
        chunk_id = data['ids'][i]
        metadata = data['metadatas'][i]

        # Extract 'name' from metadata; defaults to 'N/A' if the key doesn't exist
        name = metadata.get('name', 'N/A')

        print(f"Name: {name} | Chunk ID: {chunk_id}")

  def update_chroma_collection(self, new_chunks):
    """
    Compares new chunks against existing ones in Chroma.
    Deletes and replaces chunks if they have been updated.
    """
    # Load the existing database
    vector_store = self.get_vector_store()

    # 1. Pull all existing IDs and metadata
    existing_data = vector_store._collection.get()
    existing_ids = existing_data.get('ids', [])
    existing_metadatas = existing_data.get('metadatas', [])

    # Map a unique identifier (e.g., 'source') to the internal Chroma ID
    # This allows us to find which DB record corresponds to our new content
    id_map = {m.get('source'): i for i, m in zip(existing_ids, existing_metadatas) if m}

    ids_to_delete = []
    chunks_to_add = []

    for chunk in new_chunks:
        # Assumes metadata contains a 'source' key to identify the original file/chunk
        chunk_id_key = chunk.metadata.get('source')

        if chunk_id_key in id_map:
            # If the source exists, mark the old version for deletion
            ids_to_delete.append(id_map[chunk_id_key])

        chunks_to_add.append(chunk)

    # 2. Delete outdated records
    if ids_to_delete:
        vector_store.delete(ids=ids_to_delete)
        print(f"Deleted {len(ids_to_delete)} outdated chunks.")

    # 3. Add updated/new chunks
    if chunks_to_add:
        vector_store.add_documents(chunks_to_add)
        print(f"Added {len(chunks_to_add)} updated chunks to collection '{self.collection_name}'.")

    # Example Usage:
    # from langchain_core.documents import Document
    # sample_chunks = [Document(page_content="Updated info", metadata={"source": "person_01.txt"})]
    # update_chroma_collection(sample_chunks)

  def get_stored_pdfs(self):
    # Load the existing database
    vector_store = self.get_vector_store()
    # 3. Retrieve all documents and their metadata
    # Using the underlying collection to get all stored data
    data = vector_store.get()

    # 4. Filter for unique PDF sources
    # Documents are often split into chunks, so we use a set to get unique filenames
    pdf_documents = set()

    if 'metadatas' in data and data['metadatas']:
        for metadata in data['metadatas']:
            # Most LangChain loaders store the file path in the 'source' key
            source = metadata.get('source', '')
            if source.lower().endswith('.pdf'):
                pdf_documents.add(os.path.basename(source))

    # 5. Output the results
    if pdf_documents:
        print(f"Found {len(pdf_documents)} PDF documents in '{self.collection_name}':")
        for doc in sorted(pdf_documents):
            print(f"- {doc}")
    else:
        print(f"No PDF documents found in collection '{self.collection_name}'.")


if __name__ == "__main__":
  db = TestManager()
  db.get_stored_pdfs()
  db.list_chunks()
