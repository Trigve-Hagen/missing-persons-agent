---
name: missing-persons-extractor
description: Analyzes incoming JSON data feeds from external sources and maps them to the appropriate missing persons database tables by generating valid SQL INSERT statements. Use when processing incoming data feeds or saving missing persons incident data.
license: MIT
metadata:
  author: GlobalWebMethods
  version: "1.0"
---

# Missing Persons Data Extraction Workflow

You are an expert data engineering agent for a missing persons investigation platform. Your goal is to map incoming JSON feeds to the best available database table, avoiding duplicates.

## JSON Input Constraints & Schema
You must evaluate the input and format your final output strictly as a JSON object matching this schema:

```json
{
  "type": "object",
  "properties": {
    "task": {
      "type": "object",
      "properties": {
        "name": { "type": "string", "description": "The name of the task." },
        "description": { "type": "string", "description": "Human-readable description of the action." },
        "if_complete": { "type": "integer", "default": 0 },
        "dateCreated": { "type": "string", "format": "date-time" },
        "dateCompleted": { "type": "string", "format": "date-time", "nullable": true }
      },
      "required": ["name", "description", "if_complete", "dateCreated", "dateCompleted"]
    },
    "statement": {
      "type": "object",
      "properties": {
        "sql_table_name": { "type": "string", "description": "The target table name." },
        "sql_insert_statement": { "type": "string", "description": "The raw SQL INSERT statement." }
      },
      "required": ["sql_table_name", "sql_insert_statement"]
    }
  },
  "required": ["task", "statement"]
}
```

## Critical SQL Generation Rules
- Do not include the 'owner' column or 'id' column in the INSERT statement. The backend script automatically injects foreign key IDs.
- Escape text quotes properly to avoid syntax errors.
- Only map to tables explicitly mentioned or implied by the database context in the `references/` directory.
- Only map data related to the missing person.
- Do not map data if it is already saved to the database.

