---
name: generate-sql-leads
description: Generates valid SQL INSERT statements specifically for the leads table to capture critical tips, suspect activities, or last-known-location narrative summaries.
---

# Generate SQL Leads

## Purpose
Convert extracted citizen sightings, tips, or emergency dispatches into a precise, schema-compliant SQL `INSERT` statement optimized for the `leads` database table.

## Schema Constraints
Your generated SQL must strictly align with this schema definition:
* `id`: INTEGER, Primary Key (Omit from INSERT to allow auto-increment).
* `name`: VARCHAR / STRING (The short descriptive header or name of the note).
* `lead`: TEXT (Stores the raw narrative, text body, GPS coordinates if provided, and a reference to the agency who reported it).
* `owner`: INTEGER, Foreign Key (The ID of the person/contact the note is associated with).

## Operational Rules
1. Format all statements exclusively for the `leads` table structure.
2. Properly handle text column values by escaping embedded quotes (e.g., `don't` becomes `don''t`).
3. Compile all circumstantial information (narrative text, location lookups, and tracking metadata) cleanly into the single `lead` TEXT block parameter.
4. Automatically convert empty, missing, or unknown entity inputs to an explicit SQL `NULL`.

## Execution Steps
1. Parse the incoming JSON keys mapping to the tactical tip parameters.
2. Build an explicit column list utilizing only target headers matching the provided schema definition (`name`, `lead`, `owner`).
3. Generate and return the secure, escaped raw SQL instruction.

## Expected Output Format
Return the payload matching this exact JSON structure:
{
  "target_table": "leads",
  "generated_sql": "INSERT INTO leads (name, lead, owner) VALUES (...);"
}

## Few-Shot Examples

### Example 1: Actionable Sighting Tip
*   **Input Data**: `{"tip_title": "Central Transit Sighting", "narrative": "Subject spotted buying a transit card at the central station around 3 PM.", "owner_id": 101}`
*   **Output**:
```json
{
  "target_table": "leads",
  "generated_sql": "INSERT INTO leads (name, lead, owner) VALUES ('Central Transit Sighting', 'Subject spotted buying a transit card at the central station around 3 PM.', 101);"
}
```

### Example 2: Complex Dispatch Lead with GPS Data
*   **Input Data**: `{"tip_title": "Vehicle Sighting", "narrative": "Rusted blue sedan matching description parked outside Desert Sands Motel. GPS: 34.0522, -118.2437. Reported by LAPD Dispatched Unit 4.", "owner_id": 911}`
*   **Output**:
```json
{
  "target_table": "leads",
  "generated_sql": "INSERT INTO leads (name, lead, owner) VALUES ('Vehicle Sighting', 'Rusted blue sedan matching description parked outside Desert Sands Motel. GPS: 34.0522, -118.2437. Reported by LAPD Dispatched Unit 4.', 911);"
}
```

### Example 3: Handling String Name Regularities (Quotes)
*   **Input Data**: `{"tip_title": "Landlord's Follow-up Note", "narrative": "Landlord doesn't remember seeing anyone leave the apartment building last Tuesday night.", "owner_id": 412}`
*   **Output**:
```json
{
  "target_table": "leads",
  "generated_sql": "INSERT INTO leads (name, lead, owner) VALUES ('Landlord''s Follow-up Note', 'Landlord doesn''t remember seeing anyone leave the apartment building last Tuesday night.', 412);"
}
```
