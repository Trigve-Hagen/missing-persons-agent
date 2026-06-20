---
name: queue-sql-statement
description: Formats and outputs the final, fully escaped SQL INSERT statement required to log a staged human-review task directly into the tasks table.
---

# Queue SQL Statement

## Purpose
Take a pre-structured task payload and convert it into a valid, safe SQL `INSERT` query targeting the unified `tasks` table. This ensures all nested SQL fragments within the task are properly escaped to protect database stability.

## Operational Rules
1. Format all query strings exclusively for insertion into the `tasks` table structure.
2. Carefully double all inner single quotes (`''`) contained within the staging query parameters (`name`, `sql_insert_statement`) to avoid premature statement truncation.
3. Keep the `date_completed` database parameter explicitly set to `NULL` to indicate a pending, unexecuted queue state.

## Execution Steps
1. Parse the incoming task title, destination table name, and raw data insert query string.
2. Build an explicit database statement mapping parameters to target schema headers (`name`, `sql_table_name`, `sql_insert_statement`, `date_completed`, `if_complete`).
3. Output the fully compiled SQL instruction inside a structured data payload wrapper.

## Expected Output Format
Return the query package matching this exact JSON structure:
{
  "target_table": "tasks",
  "queued_sql_statement": "INSERT INTO tasks (name, sql_table_name, sql_insert_statement, date_completed, if_complete) VALUES (...);"
}

## Few-Shot Examples

### Example 1: Queueing an Event Staging Task
*   **Input Data**: `{"name": "Review Timeline Event: Gas Station Sighting", "sql_table_name": "events", "sql_insert_statement": "INSERT INTO events (type, name, description, date_from, owner) VALUES (4, 'Gas Station Sighting', 'Victim bought a map.', '2026-06-18 23:10:00', 101);"}`
*   **Output**:
```json
{
  "target_table": "tasks",
  "queued_sql_statement": "INSERT INTO tasks (name, sql_table_name, sql_insert_statement, date_completed, if_complete) VALUES ('Review Timeline Event: Gas Station Sighting', 'events', 'INSERT INTO events (type, name, description, date_from, owner) VALUES (4, ''Gas Station Sighting'', ''Victim bought a map.'', ''2026-06-18 23:10:00'', 101);', NULL, 0);"
}
```

### Example 2: Queueing a Telecom Link Staging Task
*   **Input Data**: `{"name": "Review Contact Phone Link: Marcus Vance Line", "sql_table_name": "phone_numbers", "sql_insert_statement": "INSERT INTO phone_numbers (type, phone_number, owner) VALUES (1, '555-0199', 204);"}`
*   **Output**:
```json
{
  "target_table": "tasks",
  "queued_sql_statement": "INSERT INTO tasks (name, sql_table_name, sql_insert_statement, date_completed, if_complete) VALUES ('Review Contact Phone Link: Marcus Vance Line', 'phone_numbers', 'INSERT INTO phone_numbers (type, phone_number, owner) VALUES (1, ''555-0199'', 204);', NULL, 0);"
}
```
