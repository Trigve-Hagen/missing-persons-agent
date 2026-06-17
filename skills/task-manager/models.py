from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from typing import Union
from enum import Enum

class Task(BaseModel):
    name: str = Field(..., description="The name of the task.")
    description: str = Field(..., description="A human-readable description of the data and action needed.")
    if_complete: int = Field(default=0, description="Default to 0.")
    dateCreated: datetime = Field(default_factory=datetime.now)
    dateCompleted: Optional[datetime] = Field(default=None)

class Statement(BaseModel):
    sql_table_name: str = Field(..., description="The name of the SQL table where the data fits best.")
    sql_insert_statement: str = Field(..., description="The exact raw SQL INSERT statement to execute.")

class ExtractionResult(BaseModel):
    task: Task
    statement: Statement

# Factory function to create the right task
def create_task(task_data: Union[EmailTask, DatabaseTask]):
    # Logic to insert into your task table goes here
    pass

class DocumentTask():
  def __init__(self, path):
    self.path = path

  def pdf_task():
    pass

  def person_task():
    pass

  def event_task():
    pass

  def note_task():
    pass
