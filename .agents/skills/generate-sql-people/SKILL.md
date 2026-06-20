---
name: generate-sql-people
description: Generates valid SQL INSERT statements specifically for the people table, mapping exact relationship types, case ownership links, and demographics.
---

# Generate SQL People

## Purpose
Convert extracted identity, demographic, and missing case status data into a precise, schema-compliant SQL `INSERT` statement optimized for the `people` table.

## Schema Constraints
Your generated SQL must strictly align with this schema definition and validation dictionary:
* `id`: INTEGER, Primary Key (Omit from INSERT to allow auto-increment).
* `first_name`: VARCHAR / STRING, Not Null.
* `middle_name`: VARCHAR / STRING, Nullable.
* `last_name`: VARCHAR / STRING, Not Null.
* `sir_name`: VARCHAR / STRING, Nullable (e.g., prefix title like Mr., Ms., Dr.).
* `suffix`: VARCHAR / STRING, Nullable (e.g., Jr., III).
* `type`: INTEGER, Nullable. Enforced lookup: `1` = Missing Person, `2` = Witness, `3` = Associate, `4` = Person of Interest, `5` = Suspect.
* `height`: INTEGER, Nullable.
* `weight`: INTEGER, Nullable.
* `hair_color`: VARCHAR / STRING, Nullable.
* `eye_color`: VARCHAR / STRING, Nullable.
* `ssn`: VARCHAR / STRING, Nullable.
* `gender`: VARCHAR / STRING, Nullable. Enforced case-insensitive string limits: `male` or `female`.
* `data_of_birth`: DATETIME, Nullable (Format: `YYYY-MM-DD HH:MM:SS`).
* `ethnicity`: VARCHAR / STRING, Nullable.
* `primary_language`: VARCHAR / STRING, Nullable.
* `missing`: DATETIME, Nullable (The exact date the victim went missing OR the date an associate met the missing person. Format: `YYYY-MM-DD HH:MM:SS`).
* `description`: TEXT, Nullable (Descriptive notes or baseline context).
* `owner`: INTEGER, Nullable (Enforced: `0` for primary missing persons, or the `id` integer of the missing person they link to).

## Classification Matrix
Evaluate the extracted text and assign exactly one of the following classifications based on the highest matching criteria.

### 🔴 Suspect
Assign this classification if any of the following apply:
* **Evidence:** Direct physical, digital, or circumstantial evidence links the individual to the disappearance.
* **Threat Profile:** The individual has a documented history of violence or has made recent threats against the missing person.
* **Deception:** The individual has provided demonstrably false timelines, alibis, or statements to investigators.

### 🟡 Person of Interest (POI)
Assign this classification if any of the following apply:
* **Proximity:** The individual is verified as the last person to see or speak with the missing person.
* **Conflict:** The individual had a recent severe argument, legal dispute, or irregular financial transaction with the missing person.
* **Unverified Timeline:** The individual has an unverified alibi or unexplained gaps in their timeline during the critical disappearance window.

### 🟢 Witness
Assign this classification if any of the following apply:
* **Observation:** The individual observed the missing person, their vehicle, or related events during the critical timeline window.
* **Firsthand Knowledge:** The individual can provide objective facts (e.g., direction of travel, clothing worn, emotional state) but has no personal motive or conflict.
* **Neutrality:** The individual has no established personal, financial, or emotional stake in the missing person's life or disappearance.

### 🔵 Associate
Assign this classification if any of the following apply:
* **Established Relationship:** The individual is a family member, friend, neighbor, classmate, or routine coworker.
* **Baseline Context:** Contact occurred outside the critical disappearance window and was routine in nature.
* **Character Data:** The individual provides background context regarding the missing person's habits, routines, or lifestyle.

## Operational Rules
1. Format all statements exclusively for the `people` table structure.
2. Translate verbal relationship types into strict integer codes (`Missing Person` -> 1, `Witness` -> 2, `Associate` -> 3, `Person of Interest` -> 4, `Suspect` -> 5).
3. Enforce valid lowercased values (`male` / `female`) for the gender assignment field.
4. Ensure all date columns (`data_of_birth`, `missing`) strictly match `YYYY-MM-DD HH:MM:SS`.
5. Escaped single quotes (`'`) properly on all textual data arguments.

## Execution Steps
1. Parse the incoming JSON keys mapping to personal demographic records.
2. Build an explicit column list utilizing only target headers matching the provided schema definition.
3. Generate and return the secure, escaped raw SQL instruction.

## Expected Output Format
Return the payload matching this exact JSON structure:
{
  "target_table": "people",
  "generated_sql": "INSERT INTO people (first_name, last_name, ...) VALUES (...);"
}

## Few-Shot Examples

### Example 1: Creating a Profile for the Primary Missing Person
*   **Input Data**: `{"first_name": "Jane", "last_name": "Doe", "relationship_type": "Missing Person", "height": 64, "weight": 125, "hair_color": "Brown", "eye_color": "Blue", "gender": "Female", "data_of_birth": "2002-04-12T00:00:00Z", "missing_date": "2026-06-18T14:30:00Z", "description": "Primary missing person contact profile."}`
*   **Output**:
```json
{
  "target_table": "people",
  "generated_sql": "INSERT INTO people (first_name, last_name, type, height, weight, hair_color, eye_color, gender, data_of_birth, missing, description, owner) VALUES ('Jane', 'Doe', 1, 64, 125, 'Brown', 'Blue', 'female', '2002-04-12 00:00:00', '2026-06-18 14:30:00', 'Primary missing person contact profile.', 0);"
}
```

### Example 2: Cataloging a Case Witness Linked to the Missing Person
*   **Input Data**: `{"sir_name": "Dr.", "first_name": "Marcus", "middle_name": "Alan", "last_name": "Vance", "relationship_type": "Witness", "gender": "Male", "primary_language": "English", "missing_person_case_id": 12}`
*   **Output**:
```json
{
  "target_table": "people",
  "generated_sql": "INSERT INTO people (sir_name, first_name, middle_name, last_name, type, gender, primary_language, owner) VALUES ('Dr.', 'Marcus', 'Alan', 'Vance', 2, 'male', 'English', 12);"
}
```

### Example 3: String Quote Escaping (Suspect Profile)
*   **Input Data**: `{"first_name": "Liam", "last_name": "O'Brian", "relationship_type": "Suspect", "description": "Subject's former partner who doesn't have an alibi.", "missing_person_case_id": 12}`
*   **Output**:
```json
{
  "target_table": "people",
  "generated_sql": "INSERT INTO people (first_name, last_name, type, description, owner) VALUES ('Liam', 'O''Brian', 5, 'Subject''s former partner who doesn''t have an alibi.', 12);"
}
```
