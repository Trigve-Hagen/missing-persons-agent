---
name: generate-sql-events
description: Generates valid SQL INSERT statements specifically for the events table to map user-defined chronological categories and precise timeline intervals.
---

# Generate SQL Events

## Purpose
Convert extracted behavioral occurrences, timeline incidents, or sightings into a precise, schema-compliant SQL `INSERT` statement optimized for the `events` database table.

## Schema Constraints
Your generated SQL must strictly align with this schema definition and validation dictionary:
* `id`: INTEGER, Primary Key (Omit from INSERT to allow auto-increment).
* `type`: INTEGER, Nullable (The user-defined category ID created in the Category database space).
* `name`: VARCHAR / STRING, Not Null (The core label or title of the event).
* `description`: TEXT, Not Null (The descriptive context or analytical details of what happened).
* `date_from`: DATETIME, Not Null (The explicit start boundary of the event window. Format: `YYYY-MM-DD HH:MM:SS`).
* `date_to`: DATETIME, Nullable (The explicit end boundary of the event window if applicable. Format: `YYYY-MM-DD HH:MM:SS`).
* `owner`: INTEGER, Not Null. Foreign Key pointing to the record index in `people(id)`.

## Operational Rules
1. Format all statements exclusively for the `events` table structure.
2. Ensure both text parameters (`name`, `description`) are escaped with doubled single quotes (`''`) to prevent database engine compilation faults.
3. Standardize incoming timestamps strictly to the database layout: `YYYY-MM-DD HH:MM:SS`.
4. If a distinct end time is not provided or can't be inferred, assign an explicit SQL `NULL` directly to the `date_to` position.

## Execution Steps
1. Parse the incoming JSON keys mapping to tactical case chronology parameters.
2. Build an explicit column list utilizing only target headers matching the provided schema definition (`type`, `name`, `description`, `date_from`, `date_to`, `owner`).
3. Generate and return the secure, escaped raw SQL instruction.

## Expected Output Format
Return the payload matching this exact JSON structure:
{
  "target_table": "events",
  "generated_sql": "INSERT INTO events (type, name, description, date_from, date_to, owner) VALUES (...);"
}

## Few-Shot Examples

### Example 1: Standard Instant Sighting Event (No End Date)
*   **Input Data**: `{"category_type_id": 4, "event_name": "Gas Station Sighting", "narrative": "Store clerk confirmed victim bought a highway map here.", "start_time": "2026-06-18T23:10:00Z", "owner_id": 101}`
*   **Output**:
```json
{
  "target_table": "events",
  "generated_sql": "INSERT INTO events (type, name, description, date_from, date_to, owner) VALUES (4, 'Gas Station Sighting', 'Store clerk confirmed victim bought a highway map here.', '2026-06-18 23:10:00', NULL, 101);"
}
```

### Example 2: Bounded Timeline Interval (With End Date)
*   **Input Data**: `{"category_type_id": 7, "event_name": "Motel Check-in Window", "narrative": "Room occupancy log registers guest presence up until checkout.", "start_time": "2026-06-15T15:00:00Z", "end_time": "2026-06-16T11:00:00Z", "owner_id": 101}`
*   **Output**:
```json
{
  "target_table": "events",
  "generated_sql": "INSERT INTO events (type, name, description, date_from, date_to, owner) VALUES (7, 'Motel Check-in Window', 'Room occupancy log registers guest presence up until checkout.', '2026-06-15 15:00:00', '2026-06-16 11:00:00', 101);"
}
```

### Example 3: Handling String Name Regularities (Quotes)
*   **Input Data**: `{"category_type_id": 2, "event_name": "Landlord's Interview", "narrative": "Stated he didn't remember seeing anyone leave the building.", "start_time": "2026-06-19T09:30:00Z", "owner_id": 204}`
*   **Output**:
```json
{
  "target_table": "events",
  "generated_sql": "INSERT INTO events (type, name, description, date_from, date_to, owner) VALUES (2, 'Landlord''s Interview', 'Stated he didn''t remember seeing anyone leave the building.', '2026-06-19 09:30:00', NULL, 204);"
}
```
