---
name: generate-sql-addresses
description: Generates valid SQL INSERT statements specifically for the addresses table, handling location metadata, integer flags, and temporal residency dates.
---

# Generate SQL Addresses

## Purpose
Convert extracted location intelligence data, residential records, and physical evidence sites into a precise, schema-compliant SQL `INSERT` statement optimized for the `addresses` database table.

## Schema Constraints
Your generated SQL must strictly align with this schema definition and validation dictionary:
* `id`: INTEGER, Primary Key (Omit from INSERT to allow auto-increment).
* `type`: INTEGER (The user-defined category ID created in the Category database space).
* `if_current`: INTEGER (Boolean flag representing if this is the active current address. Enforced values: `1` = True, `0` = False).
* `if_crime_scene`: INTEGER (Boolean flag representing if this location is an active crime scene. Enforced values: `1` = True, `0` = False).
* `name`: VARCHAR / STRING, Not Null (The user-defined nickname/label of the address, e.g., 'Primary Residence').
* `address_1`: VARCHAR / STRING, Not Null (The main street line address).
* `address_2`: VARCHAR / STRING, Nullable (The apartment, suite, or unit number).
* `city`: VARCHAR / STRING, Nullable.
* `state`: VARCHAR / STRING, Nullable.
* `zip_5`: INTEGER, Nullable (The 5-digit zip code).
* `zip_4`: INTEGER, Nullable (The +4 extended zip code suffix).
* `description`: TEXT, Nullable (General description or investigative notes).
* `date_from`: DATETIME, Nullable (The date of move-in. Format: `YYYY-MM-DD HH:MM:SS`).
* `date_to`: DATETIME, Nullable (The date of move-out. Format: `YYYY-MM-DD HH:MM:SS`).
* `owner`: INTEGER, Not Null. Foreign Key pointing to the record index in `people(id)`.

## Operational Rules
1. Format all statements exclusively for the `addresses` table structure.
2. Translate raw text boolean inputs into strict schema binary integers (`true`/`yes` -> 1, `false`/`no` -> 0). Default flags to `0` if unknown.
3. Parse and extract ZIP codes strictly as integers. Strip leading spaces, hyphens, or alphabet characters.
4. Standardize dates (`date_from`, `date_to`) to the unified system layout: `YYYY-MM-DD HH:MM:SS`.
5. Properly escape all textual payload fields containing embedded single quotes (`'`) by doubling them (`''`).

## Execution Steps
1. Parse the incoming JSON keys mapping to physical location data properties.
2. Build an explicit column list utilizing only target headers matching the provided schema definition.
3. Generate and return the secure, escaped raw SQL instruction.

## Expected Output Format
Return the payload matching this exact JSON structure:
{
  "target_table": "addresses",
  "generated_sql": "INSERT INTO addresses (type, if_current, if_crime_scene, name, ...) VALUES (...);"
}

## Few-Shot Examples

### Example 1: Standard Active Residential Address
*   **Input Data**: `{"category_type_id": 1, "current_residence": true, "crime_scene": false, "location_label": "Main Apartment", "street_1": "742 Evergreen Terrace", "street_2": "Apt 4B", "city": "Springfield", "state": "IL", "zip_code": "62704", "notes": "Primary home address.", "move_in": "2024-05-01T00:00:00Z", "owner_id": 412}`
*   **Output**:
```json
{
  "target_table": "addresses",
  "generated_sql": "INSERT INTO addresses (type, if_current, if_crime_scene, name, address_1, address_2, city, state, zip_5, zip_4, description, date_from, date_to, owner) VALUES (1, 1, 0, 'Main Apartment', '742 Evergreen Terrace', 'Apt 4B', 'Springfield', 'IL', 62704, NULL, 'Primary home address.', '2024-05-01 00:00:00', NULL, 412);"
}
```

### Example 2: Inactive Address and Active Crime Scene with Extended Zip
*   **Input Data**: `{"category_type_id": 3, "current_residence": false, "crime_scene": true, "location_label": "Sighting Location", "street_1": "100 Main St", "city": "Boston", "state": "MA", "zip_code": "02108-1234", "notes": "Abandoned vehicle found here.", "move_in": "2026-06-18T14:00:00Z", "move_out": "2026-06-18T23:30:00Z", "owner_id": 101}`
*   **Output**:
```json
{
  "target_table": "addresses",
  "generated_sql": "INSERT INTO addresses (type, if_current, if_crime_scene, name, address_1, address_2, city, state, zip_5, zip_4, description, date_from, date_to, owner) VALUES (3, 0, 1, 'Sighting Location', '100 Main St', NULL, 'Boston', 'MA', 2108, 1234, 'Abandoned vehicle found here.', '2026-06-18 14:00:00', '2026-06-18 23:30:00', 101);"
}
```

### Example 3: Handling String Name Regularities (Quotes)
*   **Input Data**: `{"category_type_id": 2, "current_residence": false, "crime_scene": false, "location_label": "Landlord's Office", "street_1": "12 Kings Road", "city": "Miami", "state": "FL", "zip_code": "33101", "owner_id": 883}`
*   **Output**:
```json
{
  "target_table": "addresses",
  "generated_sql": "INSERT INTO addresses (type, if_current, if_crime_scene, name, address_1, address_2, city, state, zip_5, zip_4, description, date_from, date_to, owner) VALUES (2, 0, 0, 'Landlord''s Office', '12 Kings Road', NULL, 'Miami', 'FL', 33101, NULL, NULL, NULL, NULL, 883);"
}
```
