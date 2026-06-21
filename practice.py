import os
import re
from typing import Annotated, TypedDict, List

# Core LangChain & LangGraph Abstractions
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
import random

class AgentState(TypedDict):
  name: int
  number: List[int]
  counter: int

def greeting_node(state: AgentState) -> AgentState:
  """ Greeting node. """
  state['name'] = f"Hello {state['name']}"
  state['counter'] = 0
  return state

def random_node(state: AgentState) -> AgentState:
  """ Generates a random number from 1 to 10. """
  state['number'].append(random.randint(0, 10))
  state['counter'] += 1
  return state

def should_continue(state: AgentState) -> AgentState:
  """ Decide to continue. """
  if state['counter'] < 5:
    print("Entering Loop", state['counter'])
    return "loop"
  else:
    return "exit"

if __name__ == "__main__":
  graph = StateGraph(AgentState)
  graph.add_node('greeting', greeting_node)
  graph.add_node('random', random_node)
  graph.add_edge('greeting', 'random')

  graph.add_conditional_edges(
    'random',
    should_continue,
    {
      'loop': 'random',
      'exit': END
    }
  )
  graph.set_entry_point('greeting')
  app = graph.compile()

  initial_state_1 = AgentState(name='Trigve', number=[], counter=-1)
  answers = app.invoke(initial_state_1)

  print(answers)


