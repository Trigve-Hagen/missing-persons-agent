from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, DateTime, Boolean, func, Text
from database.base import Base, NullToEmptyString # Import shared base

class Model(Base):
  __tablename__ = "models"
  __table_args__ = {"comment": "This table stores the model information"}

  id = Column("id", Integer, primary_key=True)
  name = Column(NullToEmptyString, comment="The name of the model.")
  model = Column(NullToEmptyString, comment="The model.")
  type = Column(NullToEmptyString, default="ollama", comment="The type of model. Allowed values are ollama and openai.")

  def __init__(self, name, model, type, system):
    self.name = name # instance
    self.model = model # model
    self.type = type  # from

class ModelParams(Base):
  __tablename__ = "model_params"
  __table_args__ = {"comment": "This table stores the model parameters if creating multiple instances of the same model."}

  id = Column("id", Integer, primary_key=True)
  name = Column(NullToEmptyString, comment="The name of the model parameter.")
  value = Column(NullToEmptyString, comment="The value of the model parameter.")
  owner = Column(Integer, ForeignKey("models.id"))

  def __init__(self, name, value, owner):
    self.name = name
    self.value = value
    self.owner = owner

class Prompt(Base):
  """
  Prompt are what the RAG LLM uses to define itself.
  """

  __tablename__ = "prompts"
  __table_args__ = {"comment": "This table stores a list of prompts for use in LLMs"}

  id = Column("id", Integer, primary_key=True)
  prompt = Column(Text, comment="The prompt for the LLM.")

  def __init__(self, prompt):
    self.prompt = prompt

class Question(Base):
  """
  Questions are the query part of RAG LLM. They are what the user would type into te chat.
  """

  __tablename__ = "questions"
  __table_args__ = {"comment": "This table stores a list of questions for use in LLMs"}

  id = Column("id", Integer, primary_key=True)
  question = Column(Text, comment="The user question for the LLM.")

  def __init__(self, question):
    self.question = question
