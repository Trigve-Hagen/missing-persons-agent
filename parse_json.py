import json
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain_core.output_parsers import JsonOutputParser

# ---------------------------------------------------------
# 1. Pydantic Schemas for Structured LLM Output
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 2. Setup LLM and Prompt Template
# ---------------------------------------------------------
# Assumes Ollama is running locally and you have a model like 'llama3' or 'mistral'
llm = Ollama(model="llama3")

system_prompt = """
You are an AI research agent analyzing missing person data feeds (JSON).
Your job is to identify relevant data, create a human-readable task for logging,
and formulate a safe, ready-to-execute SQL INSERT statement.

You have access to the following Database context (Schema chunks):
{db_schemas}

When given an input JSON, you must:
1. Extract data points related to the missing person.
2. Formulate a 'task' (name and description) to document this data.
3. Generate a SQL INSERT statement targeting the most appropriate table (from your schema context).
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "Here are the database schema chunks to guide you:\n{db_schemas}\n\nHere is the API/RSS JSON data to process:\n{json_data}")
])

# ---------------------------------------------------------
# 3. Execution Function
# ---------------------------------------------------------
def process_data(json_payload: str, db_schemas: str) -> ExtractionResult:
    # Set up parser with Pydantic schema
    parser = JsonOutputParser(pydantic_object=ExtractionResult)

    # Format the chain
    chain = prompt | llm | parser

    # Invoke the model with inputs
    result = chain.invoke({
        "db_schemas": db_schemas,
        "json_data": json_payload
    })

    return result

# ---------------------------------------------------------
# 4. Example Usage
# ---------------------------------------------------------
if __name__ == "__main__":
    # Your database chunked create statements (example)
    sample_db_schemas = """
    CREATE TABLE sightings (
        id SERIAL PRIMARY KEY,
        person_id INT,
        location TEXT,
        sighting_date TIMESTAMP,
        notes TEXT
    );
    CREATE TABLE tips (
        id SERIAL PRIMARY KEY,
        source TEXT,
        content TEXT,
        received_date TIMESTAMP
    );
    """

    # Mock data pulled from an API or RSS feed
    sample_api_json = json.dumps({
        "source": "Police Dispatch",
        "timestamp": "2026-05-29T14:30:00Z",
        "report": "Unconfirmed sighting of an individual matching the subject near 4th and Independence Ave SW, Washington, DC. Wearing a red jacket.",
        "investigator_notes": "Needs immediate follow-up and camera footage review."
    })

    print("Sending data to Ollama for processing...\n")
    agent_output = process_data(sample_api_json, sample_db_schemas)

    print(json.dumps(agent_output, indent=4))
