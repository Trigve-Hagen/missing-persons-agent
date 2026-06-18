---
name: identify-and-classify
description: Identifies a person as being a contact of the missing person and classifies them as a Witness, Associate, Person of Interest or Suspect.
license: MIT
metadata:
  author: GlobalWebMethods
  version: "1.0"
---

# Missing Person Contact Extraction and Classification

## Objective
Analyze unstructured investigative text (such as interview transcripts, case notes, and social media logs) to identify individuals who had contact with the missing person. Extract their metadata and classify their relationship level to prioritize human review.

## Core Capabilities
* **Entity Extraction:** Locate and isolate individual names, nicknames, and aliases.
* **Timeline Mapping:** Pinpoint the exact date, time, and location of the last known contact.
* **Typing & Sorting:** Apply standardized definitions to group individuals by investigative relevance.

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

## Output Schema
The agent must return a structured JSON array containing the extracted entities:

```json
[
  {
    "name": "string",
    "classification": "Suspect | Person of Interest | Witness | Associate",
    "relationship": "string",
    "last_interaction": "YYYY-MM-DDTHH:MM:SSZ",
    "location": "string",
    "rationale": "string detailing the specific criteria used for this classification"
  }
]
```

## Execution Example

### Input Text
> "Spoke with roommate Jane Vance. She states she last saw Mark at their apartment on Friday at 8:00 AM before work. She notes that Mark's ex-boyfriend, David Miller, was loitering outside the apartment building on Thursday night, which violates a restraining order Mark filed last month."

### Processed Output
```json
[
  {
    "name": "Jane Vance",
    "classification": "Associate",
    "relationship": "Roommate",
    "last_interaction": "2026-06-12T08:00:00Z",
    "location": "Shared Apartment",
    "rationale": "Roommate providing baseline timeline data. Had routine contact prior to disappearance window."
  },
  {
    "name": "David Miller",
    "classification": "Suspect",
    "relationship": "Ex-boyfriend",
    "last_interaction": "2026-06-11T22:00:00Z",
    "location": "Outside Apartment Building",
    "rationale": "Subject has an active restraining order against this individual. Individual was spotted loitering at the scene immediately prior to the disappearance, indicating a violation of law and a high-threat profile."
  }
]
```
