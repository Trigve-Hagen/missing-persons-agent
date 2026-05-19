from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, DateTime, Boolean, func, CheckConstraint, Text
from database.base import Base, NullToEmptyString # Import shared base

# This is the application state. There will only ever be one row in it.
# Some of the sites functionality uses the information saved here to run.
# Like the form that selects the processor. If you have GPU you can select to use it.
# Other parts parts of the site use it for setting up things like the Api for use in the Data Center.
# The idea is that if you set this data then the site has it to use and
# you will not have to fill it in in a form while using a page.
class State(Base):
  __tablename__ = 'state'
  __table_args__ = (
    CheckConstraint('id = 1', name='only_one_row'),
  )

  id = Column(Integer, primary_key=True, default=1)
  person = Column(Integer, default=0)
  model = Column(Integer, default=0)
  api = Column(Integer, default=0)
  prompt = Column(Integer, default=0)
  question = Column(Integer, default=0)
  processor = Column(NullToEmptyString, default="cpu")
  chunk_size = Column(Integer, default=1000)
  chunk_overlap = Column(Integer, default=200)
  root_node = Column(NullToEmptyString, default="")
  display_type = Column(NullToEmptyString, default="")
  files_size = Column(Integer, default=0)
  sql_alchemy_database_size = Column(Integer, default=0)
  chroma_database_size = Column(Integer, default=0)
  ollama_models_size = Column(Integer, default=0)

# Notices are the same as TODOs. The model is set to build 10 suggestions
# at a time for anything you ask of it. This table is where those ten
# suggestions are saved.
class Notice(Base):
  __tablename__ = "notices"

  id = Column("id", Integer, primary_key=True)
  type = Column(NullToEmptyString)
  title = Column(NullToEmptyString)
  description = Column(NullToEmptyString)
  ifComplete = Column("if_complete", Integer, default=0)
  dateCreated = Column("date_created", DateTime, server_default=func.now())

  def __init__(self, type, title, description, ifComplete):
    self.type = type
    self.title = title
    self.description = description
    self.ifComplete = ifComplete
