---
name: generate-sql-aliases
description: Generates valid SQL INSERT statements specifically for the aliases table, accommodating multi-part name variants and parent person associations.
---

# Generate SQL Aliases

## Purpose
Convert extracted moniker intelligence, pseudonyms, street names, or online aliases into a precise, schema-compliant SQL `INSERT` statement optimized for the `aliases` database table.

## Schema Constraints
Your generated SQL must strictly align with this schema definition and validation dictionary:
* `id`: INTEGER, Primary Key (Omit from INSERT to allow auto-increment).
* `first_name`: VARCHAR / STRING, Not Null (The primary pseudonym or first name variant).
* `middle_name`: VARCHAR / STRING, Nullable.
* `last_name`: VARCHAR / STRING, Nullable.
* `sir_name`: VARCHAR / STRING, Nullable (e.g., alias prefixes).
* `suffix`: VARCHAR / STRING, Nullable (e.g., alias suffixes).
* `owner`: INTEGER, Not Null. Foreign Key pointing to the record index in `people(id)`.

## Operational Rules
1. Format all statements exclusively for the `aliases` table structure.
2. Properly split full-name aliases into their respective structural fields (`first_name`, `last_name`, etc.). If a single-word moniker or nickname is extracted, assign it completely to `first_name`.
3. Properly escape any text fields containing single quotes (`'`) by doubling them (`''`) to protect database query stability.
4. Automatically convert missing or empty non-required attributes to an explicit SQL `NULL`.

## Execution Steps
1. Parse the incoming JSON keys mapping to alternate identity parameters.
2. Build an explicit column list utilizing only target headers matching the provided schema definition (`first_name`, `middle_name`, `last_name`, `sir_name`, `suffix`, `owner`).
3. Generate and return the secure, escaped raw SQL instruction.

## Expected Output Format
Return the payload matching this exact JSON structure:
{
  "target_table": "aliases",
  "generated_sql": "INSERT INTO aliases (first_name, last_name, owner) VALUES (...);"
}

## Few-Shot Examples

### Example 1: Single-Word Street Nickname Moniker
*   **Input Data**: `{"alias_full": "T-Bone", "owner_id": 204}`
*   **Output**:
```json
{
  "target_table": "aliases",
  "generated_sql": "INSERT INTO aliases (first_name, middle_name, last_name, sir_name, suffix, owner) VALUES ('T-Bone', NULL, NULL, NULL, NULL, 204);"
}
```

### Example 2: Full Alternate Persona Name Layout
*   **Input Data**: `{"sir_name": "Johnny", "first_name": "Cash", "middle_name": "Ray", "last_name": "Miller", "suffix": "III", "owner_id": 512}`
*   **Output**:
```json
{
  "target_table": "aliases",
  "generated_sql": "INSERT INTO aliases (first_name, middle_name, last_name, sir_name, suffix, owner) VALUES ('Cash', 'Ray', 'Miller', 'Johnny', 'III', 512);"
}
```

### Example 3: Handling String Name Regularities (Quotes)
*   **Input Data**: `{"first_name": "Jimmy", "last_name": "O'Toole", "owner_id": 881}`
*   **Output**:
```json
{
  "target_table": "aliases",
  "generated_sql": "INSERT INTO aliases (first_name, middle_name, last_name, sir_name, suffix, owner) VALUES ('Jimmy', NULL, 'O''Toole', NULL, NULL, 881);"
}
```
