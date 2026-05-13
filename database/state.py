from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, DateTime, Boolean, func, CheckConstraint, Text
from database.base import Base, NullToEmptyString # Import shared base

class State(Base):
  __tablename__ = 'state'
  __table_args__ = (
    CheckConstraint('id = 1', name='only_one_row'),
  )

  id = Column(Integer, primary_key=True, default=1)
  model = Column(Integer, default=0)
  person = Column(Integer, default=0)
  api = Column(Integer, default=0)
  root_node = Column(NullToEmptyString, default="")
  files_size = Column(Integer, default=0)
  sql_alchemy_database_size = Column(Integer, default=0)
  chroma_database_size = Column(Integer, default=0)
  ollama_models_size = Column(Integer, default=0)
  display_type = Column(NullToEmptyString, default="")

class Notice(Base):
  __tablename__ = "notices"

  id = Column("id", Integer, primary_key=True)
  notice = Column(Text)
  ifRead = Column(Integer, default=0)
  dateCreated = Column(DateTime)

  def __init__(self, notice, ifRead, dateCreated):
    self.notice = notice
    self.ifRead = ifRead
    self.dateCreated = dateCreated
