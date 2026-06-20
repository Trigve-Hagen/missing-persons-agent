---
name: generate-sql-files
description: Generates valid SQL INSERT statements specifically for the files table, enforcing filename uniqueness constraints and lowercased type validation values.
---

# Generate SQL Files

## Purpose
Convert extracted document metadata into a precise, schema-compliant SQL `INSERT` statement optimized for the `files` database table.

## Schema Constraints
Your generated SQL must strictly align with this schema definition and validation dictionary:
* `id`: INTEGER, Primary Key (Omit from INSERT to allow auto-increment).
* `type`: VARCHAR / STRING, Nullable. Enforced case-insensitive string limits: `image` or `pdf`.
* `filename`: VARCHAR / STRING, Not Null. Must be unique across the entire database.
* `owner`: INTEGER, Nullable. Foreign Key pointing to `people(id)`.

## Operational Rules
1. Format all statements exclusively for the `files` table structure.
2. Enforce strict, lowercased type names. Map alternate extensions to their baseline definition (`jpg`, `png`, `jpeg` -> `image` / `adobe`, `document` -> `pdf`).
3. Escaped single quotes (`'`) properly on filename parameters to prevent syntax runtime failures.
4. Automatically convert missing non-required fields to an explicit SQL `NULL`.

## Execution Steps
1. Parse the incoming JSON keys mapping to the investigative file attributes.
2. Build an explicit column list utilizing only target headers matching the provided schema definition (`type`, `filename`, `owner`).
3. Generate and return the secure, escaped raw SQL instruction.

## Expected Output Format
Return the payload matching this exact JSON structure:
{
  "target_table": "files",
  "generated_sql": "INSERT INTO files (type, filename, owner) VALUES (...);"
}

## Few-Shot Examples

### Example 1: Standard PDF Document Upload
*   **Input Data**: `{"file_type": "PDF", "file_name": "phone_dump_report.pdf", "owner_id": 101}`
*   **Output**:
```json
{
  "target_table": "files",
  "generated_sql": "INSERT INTO files (type, filename, owner) VALUES ('pdf', 'phone_dump_report.pdf', 101);"
}
```

### Example 2: Photo Attachment Map Extension Change
*   **Input Data**: `{"file_type": "jpg", "file_name": "surveillance_snapshot_04.jpg", "owner_id": 911}`
*   **Output**:
```json
{
  "target_table": "files",
  "generated_sql": "INSERT INTO files (type, filename, owner) VALUES ('image', 'surveillance_snapshot_04.jpg', 911);"
}
```

### Example 3: Handling String Name Regularities (Quotes)
*   **Input Data**: `{"file_type": "image", "file_name": "suspect's_truck_profile.png", "owner_id": 204}`
*   **Output**:
```json
{
  "target_table": "files",
  "generated_sql": "INSERT INTO files (type, filename, owner) VALUES ('image', 'suspect''s_truck_profile.png', 204);"
}
```
