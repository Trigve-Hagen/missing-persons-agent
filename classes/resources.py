import os
import json
from sqlalchemy.schema import CreateTable
from database.base import Base
from classes.model_utils import ModelUtils
from classes.model_manager import ModelManager
from classes.selections import Selection

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

  def initialize_determinator(self, engine):
    create_statements = {}

    for table_name, table in Base.metadata.tables.items():
      statement = CreateTable(table).compile(engine)
      create_statements[table_name] = str(statement)

    return create_statements

  def save_schema_to_file(self, json_data_str: str, filename: str) -> None:
    """
    Saves a raw JSON string to a validated absolute system file path.
    Creates missing parent directories automatically if they don't exist.
    """

    absolute_path = ModelUtils.resource_path(os.path.join(os.path.abspath("."), "database", filename))
    # 1. Normalize path strings to handle backslashes and forward slashes safely
    normalized_path = os.path.abspath(absolute_path)

    print(f"Normalized Path: {normalized_path}")
    # 4. Open and write the string cleanly to the targeted destination
    with open(normalized_path, 'w', encoding='utf-8') as json_file:
        json_file.write(json_data_str)

  # 2. Extract and format the schema
  def generate_agent_schema(self) -> str:
    schema_map = {}

    for mapper in Base.registry.mappers:
      cls = mapper.class_
      table = cls.__table__

      # Filter out anything not specified in our checklist
      if table.name not in Selection.data_entities:
        continue

      # Fallback to a basic template string if no Python docstring exists
      table_description = cls.__doc__.strip() if cls.__doc__ else f"Database table tracking {table.name} details."

      fields_data = {}
      for col in table.columns:
        # Clean type extraction (e.g., converts 'VARCHAR(255)' to 'STRING')
        col_type = str(col.type).split('(')[0].upper()
        if col_type == "TEXT":
          pass # Keeps TEXT clean
        elif "CHAR" in col_type or "STR" in col_type:
          col_type = "STRING"

        # Check for a column comment first, fallback to structural constraints if missing
        if col.comment:
          field_context = f"{col_type} ({col.comment})"
        else:
          # Basic backup tags if no custom comment is assigned to the model column
          backup_tags = []
          if col.primary_key: backup_tags.append("Primary Key")
          if col.foreign_keys: backup_tags.append("Foreign Key Link")
          tag_str = f" ({', '.join(backup_tags)})" if backup_tags else ""
          field_context = f"{col_type}{tag_str}"

        fields_data[col.name] = field_context

      # Construct the target top-level object key dictionary structure
      schema_map[table.name] = {
        "description": table_description,
        "fields": fields_data
      }

    json_data_str = json.dumps(schema_map, indent=2)
    self.save_schema_to_file(json_data_str, "database_contexts.json")
