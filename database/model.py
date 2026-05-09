from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, DateTime, Boolean, func
from database.base import Base, NullToEmptyString # Import shared base

class Model(Base):
  __tablename__ = "models"

  id = Column("id", Integer, primary_key=True)
  name = Column(NullToEmptyString)
  type = Column(NullToEmptyString, default="ollama")
  system = Column(NullToEmptyString)

  def __init__(self, id, name, type, system):
    self.id = id
    self.name = name # model
    self.type = type  # from
    self.system = system  # system

class ModelParams(Base):
  __tablename__ = "model_params"

  id = Column("id", Integer, primary_key=True)
  name = Column(NullToEmptyString)
  value = Column(NullToEmptyString)
  owner = Column(Integer, ForeignKey("models.id"))

  def __init__(self, id, name, value, owner):
    self.id = id
    self.name = name
    self.value = value
    self.owner = owner
