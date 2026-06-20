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
  theme = Column(NullToEmptyString, default="light", comment="The name of the theme. Allowed values are light and dark.")
  person = Column(Integer, default=0, comment="The id of the Person entity active in state.")
  model = Column(Integer, default=0, comment="The id of the Model entity active in state.")
  api = Column(Integer, default=0, comment="The id of the Api set entity active in state.")
  prompt = Column(Integer, default=0, comment="The id of the Prompt set entity active in state.")
  question = Column(Integer, default=0, comment="The id of the Question set entity active in state.")
  database = Column(NullToEmptyString, default="investigation_db", comment="The name of the vector database active in state. Allowed values are texts_db, images_db.")
  collection = Column(NullToEmptyString, default="missing_persons", comment="The collection in active in state. Allowed values are missing_persons, databases and investigator.")
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

class Task(Base):
  """
  Tasks are TODOs.
  """

  __tablename__ = "tasks"
  __table_args__ = {"comment": "This table stores the site tasks."}

  id = Column("id", Integer, primary_key=True)
  name = Column(NullToEmptyString, comment="The name of the task.")
  sqlTableName = Column("sql_table_name", NullToEmptyString, default="", comment="The name of the sql table name where the data will be inserted.")
  sqlInsertStatement = Column("sql_insert_statement", NullToEmptyString, default="", comment="The sql insert statement.")
  dateCreated = Column("date_created", DateTime, server_default=func.now(), comment="The date the task was created.")
  dateCompleted = Column("date_completed", DateTime, default=None, comment="The date the task was created.")
  ifComplete = Column("if_complete", Integer, default=0, comment="If the task has been completed. Allowed values are 0 for no and 1 for yes.")

  def __init__(self, name, sqlTableName, sqlInsertStatement, dateCreated, dateCompleted, ifComplete):
    self.name = name
    self.sqlTableName = sqlTableName
    self.sqlInsertStatement = sqlInsertStatement
    self.dateCreated = dateCreated
    self.dateCompleted = dateCompleted
    self.ifComplete = ifComplete
