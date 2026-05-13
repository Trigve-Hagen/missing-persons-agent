import os
from sqlalchemy import create_engine, inspect, exc, select, update
from database.state import State
from database.category import Category
from database.event import Event, Url, Question
from database.news import News
from database.apis import Api, ApiField
from database.person import Person, Alias, Email, Phone, Address
from ollama_manager import OllamaManager

class Resources():
  def __init__(self, session):
    self.session = session
    self.base_path = os.path.abspath(".")

  def get_folder_size(self, folder_path):
    total_size = 0
    path = os.path.join(self.base_path, folder_path)
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            # Only count if it's a file and not a symbolic link
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
    return total_size

  def get_file_size(self, file_path):
    total_size = 0
    path = os.path.join(self.base_path, file_path)
    print(path)
    if os.path.isfile(path):
      total_size = os.path.getsize(path)
    return total_size

  def files_size(self):
    size_in_bytes = self.get_folder_size('')
    return f"{(size_in_bytes / (1024*1024)) / 1000:.2f} GB"

  def sql_alchemy_database(self):
    size_in_bytes = self.get_file_size('database\\sql_alchemy\\database.db')
    print(size_in_bytes)
    return f"{size_in_bytes / (1024*1024):.2f} MB"

  def chroma_database(self):
    size_in_bytes = self.get_file_size('database\\chroma_db\\chroma.sqlite3')
    print(size_in_bytes)
    return f"{size_in_bytes / (1024*1024):.2f} MB"

  def ollama_models(self):
    manager = OllamaManager(session=self.session)
    models = manager.get_models()
    return models

  def ollama_models_size(self):
    manager = OllamaManager(session=self.session)
    return f"{manager.get_ollama_storage_gb():.2f} GB"
