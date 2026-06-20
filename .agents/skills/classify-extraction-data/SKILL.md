---
name: classify-extraction-data
description: Analyzes raw text or documents to identify entities, events, or leads relevant to a missing person investigation and maps them to the correct database table.
license: MIT
metadata:
  author: GlobalWebMethods
  version: "1.0"
---

# Classify Extraction Data

## Purpose
Analyze incoming raw text from missing person investigations. Your job is to identify the core type of information being discussed and map it strictly to one of the eight destination tables.

## Classification Rules
Evaluate the `raw_investigation_data` and select exactly ONE target table based on these strict definitions:

1. **`people`**: Information about the missing individual, or names/details of their direct contacts.
2. **`aliases`**: Alternate names, street names, online handles, or pseudonyms used specifically by the contacts.
3. **`addresses`**: Physical locations, residential addresses, workplaces, or mailing addresses tied to a contact.
4. **`phone_numbers`**: Landlines, mobile numbers, or VoIP numbers utilized by a contact.
5. **`email_addresses`**: Digital email addresses utilized by a contact.
6. **`events`**: Sightings, incidents, phone calls, check-ins, or actions with a specific timestamp used to build an investigative timeline.
7. **`files`**: References to physical or digital evidence, photos, audio recordings, or document attachments.
8. **`leads`**: High-priority tactical data indicating actionable next steps, specifically descriptions of where the missing person was last seen or potential foul play.

## Execution Steps
1. Read the input text thoroughly.
2. Identify the primary entity or action. If multiple types exist, prioritize `leads` or `events` first, then break down individual entities in separate runs.
3. Output the exact string name of the `target_table`.
4. Extract the relevant key-value pairs from the text into a clean JSON format matching the logical fields of that table.

## Expected Output Format
Return your analysis in this exact JSON structure:
{
  "target_table": "table_name_here",
  "extracted_entities": {
    "field_1": "value_1",
    "field_2": "value_2"
  },
  "confidence_score": 0.00
}

## Few-Shot Examples

### Example 1: Prioritizing a Timeline Event
*   **Input**: "On November 14, 2025, at approximately 10:15 PM, Jane's phone pinged a tower near the marina, right before her phone was turned off."
*   **Output**:
```json
{
  "target_table": "events",
  "extracted_entities": {
    "event_type": "phone_ping",
    "timestamp": "2025-11-14T22:15:00Z",
    "location_description": "Near the marina",
    "notes": "Phone was turned off immediately after this ping."
  },
  "confidence_score": 0.98
}
```

### Example 2: Extracting a High-Priority Lead
*   **Input**: "An anonymous tipster claims they saw a person matching the flyer's description getting into a rusted blue sedan outside the 7-Eleven on 5th Street on Tuesday night."
*   **Output**:
```json
{
  "target_table": "leads",
  "extracted_entities": {
    "lead_source": "anonymous_tip",
    "description": "Saw person matching flyer description getting into a rusted blue sedan",
    "last_seen_location": "7-Eleven on 5th Street",
    "approximate_time": "Tuesday night",
    "actionable": true
  },
  "confidence_score": 0.95
}
```

### Example 3: Extracting Contact Information (People & Phone)
*   **Input**: "We spoke to the missing person's roommate, Marcus Vance. He can be reached at 555-0199."
*   **Output**:
```json
{
  "target_table": "people",
  "extracted_entities": {
    "full_name": "Marcus Vance",
    "relationship_to_missing": "Roommate",
    "associated_phone": "555-0199"
  },
  "confidence_score": 0.92
}
```
