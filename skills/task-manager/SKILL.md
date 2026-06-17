---
name: task-manager
description: Creates a task that when completed will add the data collected to a database table.
---

# Task Manager Skill

## When to use this skill
Use this skill when collected data needs to be added to a relational database table.

## How to Use this Skill
This skill provides the `create_pdf_task()` function from the `create_tasks.py` script. Import it into your agent script:

python
from skills.create_tasks import create_pdf_task

result = create_pdf_task(
    file_path="https://full.com/path/to/document.pdf"
)

### Parameters
- `file_path` (str): Absolute path to the PDF file

### Returns
JSON object with:
- `success` (bool): Whether creating the task succeeded
- `file_path` (str): Path to the processed file
