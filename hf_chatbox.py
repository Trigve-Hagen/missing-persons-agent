import os
import signal
import sys
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

# Load variables from .env into the system environment
load_dotenv()
gemini_key = os.getenv("GEMINI_KEY")

def signal_handler(sif, frame):
  print("\nThanks for using Gemini. :)")
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def generate_rag_prompt(query, context):
  escaped = context.replace("'","").replace('"',"").replace("\n"," ")
  prompt = ("""
            You are a helpful and informative bot that answers questions using text from the reference context included below. Be sure to repond in complete sentences, being comprehensive, include all relevent background information. However you are talking to a non-technical audience, so be sure to break down complicated concepts and \
            strike a friendly and conversational tone. If the context is irrelevant to the answer, you may ignore it.
            QUESTION: '{query}'
            CONTEXT: '{context}'

            ANSWER:
            """).format(query=query, context=context)
  return prompt

def get_relevant_context_from_db(query):
  context = ""
  embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})
  vector_db = Chroma(persist_directory="./chroma_db_nccn", embedding_function=embedding_function)
  search_results = vector_db.similarity_search(query, k=6)
  for result in search_results:
    context += result.page_content + "\n"
  return context

while True:
  print("_________________________________________________")
  print("What would you like ask?")
  query = input("Query: ")
  context = get_relevant_context_from_db(query)
  prompt = generate_rag_prompt(query=query, context=context)
  print(prompt)
