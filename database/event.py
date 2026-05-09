from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, DateTime, Boolean, func
from database.base import Base, NullToEmptyString # Import shared base

class Url(Base):
  __tablename__ = "urls"

  id = Column("id", Integer, primary_key=True)
  name = Column(NullToEmptyString)
  url = Column(NullToEmptyString)

  def __init__(self, name, url):
    self.name = name
    self.url = url

class Question(Base):
  __tablename__ = "questions"

  id = Column("id", Integer, primary_key=True)
  question = Column(NullToEmptyString)

  def __init__(self, question):
    self.question = question

class Event(Base):
  __tablename__ = "events"

  id = Column("id", Integer, primary_key=True)
  eventType = Column(NullToEmptyString)
  description = Column(NullToEmptyString)
  owner = Column(Integer, ForeignKey("people.id"))

  def __init__(self, ieventType, description, owner):
    self.eventType = eventType
    self.description = description
    self.owner = owner
