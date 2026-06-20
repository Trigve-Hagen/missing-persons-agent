---
name: generate-sql-email-addresses
description: Generates valid SQL INSERT statements specifically for the email_addresses table, enforcing strict type integers, string limits, and owner foreign keys.
---

# Generate SQL Email Addresses

## Purpose
Convert extracted electronic mail intelligence into a precise, schema-compliant SQL `INSERT` statement optimized for the `email_addresses` database table.

## Schema Constraints
Your generated SQL must strictly align with this schema definition and validation dictionary:
* `id`: INTEGER, Primary Key (Omit from INSERT to allow auto-increment).
* `type`: INTEGER (The user-defined category ID created in the Category database space).
* `email_address`: VARCHAR(255) / STRING, Not Null. Maximum 255 characters.
* `owner`: INTEGER, Not Null. Foreign Key pointing to the record index in `people(id)`.

## Operational Rules
1. Format all statements exclusively for the `email_addresses` table structure.
2. Standardize input emails to lowercase when creating the SQL insertion script to maintain data cleanliness.
3. Truncate or clean the `email_address` string to guarantee it does not exceed the 255-character database ceiling.
4. Properly escape any special characters or single quotes (`'`) if they appear in unusual mailbox names.

## Execution Steps
1. Parse the incoming JSON keys mapping to digital email parameters.
2. Build an explicit column list utilizing only target headers matching the provided schema definition (`type`, `email_address`, `owner`).
3. Generate and return the secure, escaped raw SQL instruction.

## Expected Output Format
Return the payload matching this exact JSON structure:
{
  "target_table": "email_addresses",
  "generated_sql": "INSERT INTO email_addresses (type, email_address, owner) VALUES (...);"
}

## Few-Shot Examples

### Example 1: Standard Personal Email Account
*   **Input Data**: `{"category_type_id": 1, "email_address": "johndoe@gmail.com", "owner_id": 142}`
*   **Output**:
```json
{
  "target_table": "email_addresses",
  "generated_sql": "INSERT INTO email_addresses (type, email_address, owner) VALUES (1, 'johndoe@gmail.com', 142);"
}
```

### Example 2: Enterprise Work Email with Mixed Casing
*   **Input Data**: `{"category_type_id": 2, "email_address": "MARK.VANCE@CORPHQ.COM", "owner_id": 305}`
*   **Output**:
```json
{
  "target_table": "email_addresses",
  "generated_sql": "INSERT INTO email_addresses (type, email_address, owner) VALUES (2, 'mark.vance@corphq.com', 305);"
}
```

### Example 3: Handling Rare Mailbox Name Characters (Quotes)
*   **Input Data**: `{"category_type_id": 3, "email_address": "officer.o'brian@state.gov", "owner_id": 881}`
*   **Output**:
```json
{
  "target_table": "email_addresses",
  "generated_sql": "INSERT INTO email_addresses (type, email_address, owner) VALUES (3, 'officer.o''brian@state.gov', 881);"
}
```
