from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, DateTime, Boolean, func, CheckConstraint, Text
from database.base import Base, NullToEmptyString # Import shared base

class State(Base):
  """
  This is the application state. There will only ever be one row in it.
  Some of the sites functionality uses the information saved here to run.
  Like the form that selects the processor. If you have GPU you can select to use it.
  Other parts parts of the site use it for setting up things like the Api for use in the Data Center.
  The idea is that if you set this data then the site has it to use and
  you will not have to fill it in in a form while using a page.
  """

  __tablename__ = 'state'
  __table_args__ = {"comment": "This table stores the applications state information"}
  __table_args__ = (
    CheckConstraint('id = 1', name='only_one_row'),
  )

  id = Column(Integer, primary_key=True, default=1)
  person = Column(Integer, default=0, comment="The id of the Person entity active in state.")
  model = Column(Integer, default=0, comment="The id of the Model entity active in state.")
  api = Column(Integer, default=0, comment="The id of the Api set entity active in state.")
  prompt = Column(Integer, default=0, comment="The id of the Prompt set entity active in state.")
  question = Column(Integer, default=0, comment="The id of the Question set entity active in state.")
  database = Column(NullToEmptyString, default="investigation_db", comment="The name of the vector database active in state. Allowed values are investigation_db and code_optimize_db.")
  processor = Column(NullToEmptyString, default="cpu", comment="The name of the processor active in state. Allowed values are in the Selection class available_devices property.")
  loader = Column(NullToEmptyString, default="docling", comment="The name of the document loader active in state.")
  chunk_size = Column(Integer, default=1000, comment="The chunk size of the document splitter active in state.")
  chunk_overlap = Column(Integer, default=200, comment="The chunk overlap of the document splitter active in state.")
  root_node = Column(NullToEmptyString, default="", comment="The regex used to parse json nodes in Data Center.")
  display_type = Column(NullToEmptyString, default="", comment="The display type in Data Center. Allowed values are json and table.")
  files_size = Column(Integer, default=0, comment="The size of all the files in the code base. For use in keeping track of the memory used.")
  sql_alchemy_database_size = Column(Integer, default=0, comment="The size of the sql alchemy database. For use in keeping track of the memory used.")
  chroma_database_size = Column(Integer, default=0, comment="The size of the vector chroma database. For use in keeping track of the memory used.")
  ollama_models_size = Column(Integer, default=0, comment="The size of all the ollama models. For use in keeping track of the memory used.")

class Notice(Base):
  """
  Notices are the same as TODOs. The model is set to build 10 suggestions
  at a time for anything you ask of it. This table is where those ten
  suggestions are saved.
  """

  __tablename__ = "notices"
  __table_args__ = {"comment": "This table stores the site notices. Notices are created from the suggestions when optimizing the investigation or the code."}

  id = Column("id", Integer, primary_key=True)
  type = Column(NullToEmptyString, comment="The type of the notice. Allowed values are code, and investigation.")
  title = Column(NullToEmptyString, comment="The title of the notice.")
  description = Column(NullToEmptyString, comment="The description of the notice.")
  ifComplete = Column("if_complete", Integer, default=0, comment="If the notice has been completed. Allowed values are 0 for no and 1 for yes.")
  dateCreated = Column("date_created", DateTime, server_default=func.now(), comment="The date the notice was created.")

  def __init__(self, type, title, description, ifComplete):
    self.type = type
    self.title = title
    self.description = description
    self.ifComplete = ifComplete
