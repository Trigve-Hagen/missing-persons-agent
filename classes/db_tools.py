from langchain_core.tools import tool

class DatabaseService:
    def __init__(self, connection_string: str):
        # Share this connection across multiple tools
        self.connection = connection_string

    @tool
    def fetch_user_age(self, username: str) -> str:
        """Look up a user's age in the database."""
        # Action logic using self.connection goes here
        return f"Age of {username} fetched from {self.connection}"

    @tool
    def update_user_status(self, username: str, status: str) -> str:
        """Update a user's status profile."""
        return f"Status updated to {status}"

# --- Usage ---
# db_service = DatabaseService(connection_string="postgresql://localhost:5432")

# Pass the instantiated methods directly to your LangChain agent
# tools = [db_service.fetch_user_age, db_service.update_user_status]
