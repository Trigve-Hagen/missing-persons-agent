import os
import json
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableMap
from classes.model_utils import ModelUtils
from langchain_core.tools import tool

@tool
def get_current_weather(location):
  """Get the current weather for a specific city location.

  Args:
      location: The name of the city, e.g., 'San Francisco'
  """
  weather_info = {
    "location": location,
    "temperature": "72",
    "unit": "fahrenheit",
    "forcast": ["sunny", "windy"],
  }
  return json.dumps(weather_info)

class ChatTester():

  def get_vector_store(self):
    return Chroma(
      persist_directory=ModelUtils.resource_path(os.path.join("database", "investigation_db")),
      collection_name="missing_persons",
      embedding_function=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    )

  def chatTime(self):
    template = """Answer the question based only on the following context
    {context}

    Question: {question}
    """

    prompt = ChatPromptTemplate.from_messages([
      ("system", "You are an expert assistant. You have access to tools. "
               "If the user asks about the weather, you MUST use the get_current_weather tool. "
               "Do not answer from memory."),
      ("human", "{input}")
    ])
    model = ChatOllama(
      model='llama3-groq-tool-use',
      temperature=0,
    )
    model.bind_tools(tools=[get_current_weather])
    output_parser = StrOutputParser()

    chain = prompt | model

    return chain.invoke({
      "input": "what is the weather in SF?"
    })

if __name__ == "__main__":
  chat = ChatTester()
  print(chat.chatTime())
