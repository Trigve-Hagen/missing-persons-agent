import os
from sqlalchemy.schema import CreateTable
from database.base import Base
from classes.model_utils import ModelUtils
from classes.model_manager import ModelManager

class Resources():
  def get_folder_size(self, folder_path):
    total_size = 0
    path = os.path.join(os.path.abspath("."), folder_path)
    for root, dirs, files in os.walk(path):
      for file in files:
        file_path = os.path.join(root, file)
        if os.path.isfile(file_path):
          total_size += os.path.getsize(file_path)
    return total_size

  def get_file_size(self, file_path):
    total_size = 0
    path = ModelUtils.resource_path(os.path.join(os.path.abspath("."), file_path))
    if os.path.isfile(path):
      total_size = os.path.getsize(path)
    return total_size

  def files_size(self):
    size_in_bytes = self.get_folder_size('')
    return f"{(size_in_bytes / (1024*1024)) / 1000:.2f} GB"

  def sql_alchemy_database(self):
    size_in_bytes = self.get_file_size(os.path.join("database", "sql_alchemy", "database.db"))
    print(size_in_bytes)
    return f"{size_in_bytes / (1024*1024):.2f} MB"

  def chroma_database(self):
    size_in_bytes = self.get_file_size(os.path.join("database", "investigation_db", "chroma.sqlite3"))
    print(size_in_bytes)
    return f"{size_in_bytes / (1024*1024):.2f} MB"

  def ollama_models(self):
    manager = ModelManager()
    models = manager.get_models()
    return models

  def ollama_models_size(self):
    manager = ModelManager()
    return f"{manager.get_ollama_storage_gb():.2f} GB"

  """ def initialize_determinator(self, engine):
    create_statements = {}

    for table_name, table in Base.metadata.tables.items():
      statement = CreateTable(table).compile(engine)
      create_statements[table_name] = str(statement)

    return create_statements """
