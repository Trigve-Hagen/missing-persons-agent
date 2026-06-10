from langchain_core.tools import tool
from database.state import Task

class DatabaseService:

  def __init__(self, session):
    self.session = session

  @tool
  def create_task_row(self, name: str, description: str = "") -> str:
    """
    Creates a new task record in the tasks database.
    Use this tool whenever the user explicitly requests to create, add, or log a task.
    """

    try:
      new_task = Task(name=name, description=description, is_completed=0)
      self.session.add(new_task)
      self.session.commit()
      return f"Success: Task '{name}' has been created with ID {new_task.id}."
    except Exception as e:
      self.session.rollback()
      return f"Error creating task: {str(e)}"
    finally:
      self.session.close()

  @tool
  def update_user_status(self, username: str, status: str) -> str:
    """Update a user's status profile."""
    return f"Status updated to {status}"

# --- Usage ---
# db_service = DatabaseService(connection_string="postgresql://localhost:5432")

# Pass the instantiated methods directly to your LangChain agent
# tools = [db_service.fetch_user_age, db_service.update_user_status]
