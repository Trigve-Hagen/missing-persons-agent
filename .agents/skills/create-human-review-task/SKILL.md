---
name: create-human-review-task
description: Coordinates and formats a structured human review payload by matching a pre-compiled target SQL insert query with an actionable review description.
---

# Create Human Review Task

## Purpose
Format a unified staging payload for human operator verification. This skill acts as the final preparation step, taking the target destination table name and its pre-built data query, and wrapping them into a clean review envelope.

## Operational Rules
1. Rely entirely on the output of the downstream table-specific SQL generator skills.
2. Construct distinct, descriptive task titles based on the destination context so human investigators can easily triage the queue.
3. Explicitly initialize status metrics such as `if_complete` to `0` and map chronological completion benchmarks to `NULL`.

## Execution Steps
1. Accept the validated target SQL table name and the pre-built child `INSERT` statement.
2. Formulate a short, distinct task title (e.g., "Review New Sighting Lead" or "Verify Phone Registration").
3. Return a clean, structured JSON object containing all necessary values to feed directly into a task execution handler.

## Expected Output Format
Return your data package matching this exact JSON structure:
{
  "task_payload": {
    "name": "Action-oriented task title",
    "sql_table_name": "target_table_name",
    "sql_insert_statement": "INSERT INTO table ...",
    "date_completed": null,
    "if_complete": 0
  }
}

## Few-Shot Examples

### Example 1: Creating a Staged Event Review
*   **Input Destination Table**: `events`
*   **Input Pre-Built Query**: `INSERT INTO events (type, name, description, date_from, date_to, owner) VALUES (4, 'Gas Station Sighting', 'Victim bought a highway map.', '2026-06-18 23:10:00', NULL, 101);`
*   **Output**:
```json
{
  "task_payload": {
    "name": "Review Timeline Event: Gas Station Sighting",
    "sql_table_name": "events",
    "sql_insert_statement": "INSERT INTO events (type, name, description, date_from, date_to, owner) VALUES (4, 'Gas Station Sighting', 'Victim bought a highway map.', '2026-06-18 23:10:00', NULL, 101);",
    "date_completed": null,
    "if_complete": 0
  }
}
```

### Example 2: Creating a Staged Critical Lead Review
*   **Input Destination Table**: `leads`
*   **Input Pre-Built Query**: `INSERT INTO leads (name, lead, owner) VALUES ('Vehicle Sighting', 'Rusted blue sedan with dented door.', 911);`
*   **Output**:
```json
{
  "task_payload": {
    "name": "Review Critical Lead: 7-Eleven Vehicle Sighting",
    "sql_table_name": "leads",
    "sql_insert_statement": "INSERT INTO leads (name, lead, owner) VALUES ('Vehicle Sighting', 'Rusted blue sedan with dented door.', 911);",
    "date_completed": null,
    "if_complete": 0
  }
}
```

### Example 3: Creating a Staged Telecom Entry Review
*   **Input Destination Table**: `phone_numbers`
*   **Input Pre-Built Query**: `INSERT INTO phone_numbers (type, phone_number, owner) VALUES (1, '555-0199', 204);`
*   **Output**:
```json
{
  "task_payload": {
    "name": "Review Contact Phone Link: Marcus Vance Line",
    "sql_table_name": "phone_numbers",
    "sql_insert_statement": "INSERT INTO phone_numbers (type, phone_number, owner) VALUES (1, '555-0199', 204);",
    "date_completed": null,
    "if_complete": 0
  }
}
```
