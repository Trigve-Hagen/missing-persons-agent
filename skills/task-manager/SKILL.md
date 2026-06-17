---
name: task-manager
description: Creates a task and statement for inserting data into a relation database.
---

# Task Manager Skill

## When to use this skill
Use this skill when collected data needs to be added to a database table.

## How to Use this Skill
This skill provides the `create_pdf_task()`, `create_person_task()`, `create_event_task()` and the `create_note_task()` functions from the `create_tasks.py` script. Import it into your agent script:

python
from skills.task_manager.create_tasks import create_pdf_task, create_person_task, create_event_task, create_note_task
