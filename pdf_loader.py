# https://www.youtube.com/watch?v=aTqDvi39yQg

from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader, TextLoader, DirectoryLoader, PythonLoader, UnstructuredHTMLLoader
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.bedrock import BedrockEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

import os
import tempfile
import uuid
import pandas as pd
import re


loaders = [PyPDFLoader(os.path.join(os.path.abspath("."), 'assets/files/Trigve-Hagen_04272026_1778569712322929200.pdf'))]

docs = []

for file in loaders:
  docs.extend(file.load())

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(docs)
embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})

vectorstore = Chroma.from_documents(docs, embedding_function, persist_directory="./chroma_db_nccn")

print(vectorstore._collection.count())

# import all code files
""" pyloader = DirectoryLoader(
  resource_path(),
  glob="**/*.py",
  loader_cls=PythonLoader
)

htmlloader = DirectoryLoader(
  resource_path('templates'),
  glob="**/*.html",
  loader_cls=UnstructuredHTMLLoader
)

dbloader = DirectoryLoader(
  resource_path('database'),
  glob="**/*.py",
  loader_cls=PythonLoader
) """

""" def load_documents():
  document_loader = PyPDFDirectoryLoader(DATA_PATH)
  return document_loader.load()

def split_documents(documents: list[Document]):
  text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=80,
    length_function=len,
    is_separator_regex=False
  )
  return text_splitter.split_documents(documents)

def get_embedding_function():
  embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
  )
  return embeddings """

""" def get_embedding_function():
  embeddings = BedrockEmbeddings(
    credentials_profile_name="default", region_name="us-east-1"
  )
  return embeddings """

""" def add_to_chroma(chunks: list[Document]):
  db = Chroma(
    persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
  )
  db.add_documents(new_chunks, ids=new_chunk_ids)
  db.persist() """

# documents = load_documents()
# chunks = split_documents(documents)
# print(chunks)

