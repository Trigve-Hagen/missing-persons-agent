---
name: generate-sql-phone-numbers
description: Generates valid SQL INSERT statements specifically for the phone_numbers table adhering to strict type integers, string limits, and owner foreign keys.
---

# Generate SQL Phone Numbers

## Purpose
Convert extracted telecommunication intelligence into a precise SQL `INSERT` statement optimized for the `phone_numbers` database schema. This skill ensures strict enforcement of data types, string length limits, and parent-child relational keys.

## Schema Constraints
Your generated SQL must strictly align with this schema definition:
* `id`: INTEGER, Primary Key (Omit from INSERT to allow auto-increment, or pass explicitly if required).
* `type`: INTEGER (Enumerated type: 1 = Mobile, 2 = Landline, 3 = Burner/Other).
* `phone_number`: VARCHAR(20), Not Null. Maximum 20 characters.
* `owner`: INTEGER, Not Null. Foreign Key pointing to `people(id)`.

## Operational Rules
1. Format all statements exclusively for the `phone_numbers` table structure.
2. Translate text-based phone types into their respective schema integers (`mobile` -> 1, `landline` -> 2, `burner`/`other` -> 3).
3. Truncate or clean the `phone_number` string to guarantee it does not exceed the 20-character database ceiling.

## Execution Steps
1. Parse the incoming JSON keys mapping to telecom parameters.
2. Build an explicit column list matching the exact schema variables (`type`, `phone_number`, `owner`).
3. Generate and return the secure, escaped raw SQL instruction.

## Expected Output Format
Return the payload matching this exact JSON structure:
{
  "target_table": "phone_numbers",
  "generated_sql": "INSERT INTO phone_numbers (type, phone_number, owner) VALUES (...);"
}

## Few-Shot Examples

### Example 1: Standard Mobile Number (Type 1)
*   **Input Data**: `{"phone_type": "mobile", "phone_number": "555-0199", "owner_id": 204}`
*   **Output**:
```json
{
  "target_table": "phone_numbers",
  "generated_sql": "INSERT INTO phone_numbers (type, phone_number, owner) VALUES (1, '555-0199', 204);"
}
```

### Example 2: Residential Landline (Type 2)
*   **Input Data**: `{"phone_type": "landline", "phone_number": "+1-800-555-0100", "owner_id": 105}`
*   **Output**:
```json
{
  "target_table": "phone_numbers",
  "generated_sql": "INSERT INTO phone_numbers (type, phone_number, owner) VALUES (2, '+1-800-555-0100', 105);"
}
```

### Example 3: Burner Account with Long String Truncation (Type 3)
*   **Input Data**: `{"phone_type": "burner", "phone_number": "+1(555)999-0412 ext 9999", "owner_id": 911}`
*   **Notes**: String length is 24 characters; must be cleaned/truncated to stay under the VARCHAR(20) constraint.
*   **Output**:
```json
{
  "target_table": "phone_numbers",
  "generated_sql": "INSERT INTO phone_numbers (type, phone_number, owner) VALUES (3, '+15559990412', 911);"
}
```
