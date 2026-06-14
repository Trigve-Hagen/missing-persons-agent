import sqlite3
import json
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama

# ==========================================
# 1. SETUP LOCAL TASK DATABASE
# ==========================================
def init_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            ifcomplete INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()

# DB Helper to insert records
def insert_task(name: str, description: str, ifcomplete: int):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (name, description, ifcomplete) VALUES (?, ?, ?)",
        (name, description, ifcomplete)
    )
    conn.commit()
    conn.close()
    print(f"\n[DB SUCCESS] Inserted Task: Name='{name}', Status={ifcomplete}")


# ==========================================
# 2. DEFINE SYSTEM ARCHITECTURE AND STATE
# ==========================================
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    json_string: str
    parsed_data: dict
    current_iteration: int
    max_iterations: int


# Use langchain-ollama package natively to call deepseek-r1
llm = ChatOllama(model="deepseek-r1", temperature=0)


# ==========================================
# 3. DEFINE WORKFLOW NODES
# ==========================================
def parse_json_node(state: AgentState):
    """
    Asks DeepSeek to extract structured attributes from the raw string variable.
    """
    raw_str = state["json_string"]

    prompt = (
        f"You are a strict data parsing worker. Extract the data payload out of this string: '{raw_str}'. "
        "Format your answer directly as a clean minified JSON object with keys: "
        "'name' (string), 'description' (string), and 'ifcomplete' (integer 1 or 0). "
        "Do not output codeblocks, markdown formatting, or any preamble."
    )

    # Run the model logic
    response = llm.invoke([HumanMessage(content=prompt)])

    # Strip any potential deepseek thought blocks <think>...</think> if present
    content = response.content
    if "</think>" in content:
        content = content.split("</think>")[-1].strip()

    try:
        data = json.loads(content)
        return {
            "messages": [response],
            "parsed_data": data,
            "current_iteration": state["current_iteration"] + 1
        }
    except json.JSONDecodeError:
        # Loop fallback: Pass structural error to state history to let the model self-correct next pass
        error_msg = AIMessage(content=f"Failed to parse target JSON from output: {content}")
        return {
            "messages": [error_msg],
            "current_iteration": state["current_iteration"] + 1
        }


def save_to_database_node(state: AgentState):
    """
    Executes when the iterative validation condition passes. Writes payload directly to DB.
    """
    data = state["parsed_data"]

    # Map fields dynamically to the columns
    name = data.get("name", "Untitled Task")
    description = data.get("description", "No description provided.")
    ifcomplete = int(data.get("ifcomplete", 0))

    insert_task(name, description, ifcomplete)
    return {"messages": [AIMessage(content="Task saved successfully.")] }


# ==========================================
# 4. CONDITIONAL ROUTER (Iterative Safety Switch)
# ==========================================
def router_decision(state: AgentState):
    """
    Determines if parsing succeeded, or loops back to correct errors up to max limit.
    """
    if state["parsed_data"]:
        return "save_node"

    if state["current_iteration"] >= state["max_iterations"]:
        print("\n[SYSTEM WARN] Maximum iterations reached without valid JSON formatting.")
        return END

    return "parse_node"


# ==========================================
# 5. COMPILE THE SYSTEM GRAPH
# ==========================================
workflow = StateGraph(AgentState)

workflow.add_node("parse_node", parse_json_node)
workflow.add_node("save_node", save_to_database_node)

workflow.add_edge(START, "parse_node")

workflow.add_conditional_edges(
    "parse_node",
    router_decision,
    {
        "save_node": "save_node",
        "parse_node": "parse_node",
        END: END
    }
)
workflow.add_edge("save_node", END)

app = workflow.compile()


# ==========================================
# 6. RUN THE PIPELINE
# ==========================================
# Input string containing messy JSON data
raw_json_input = "{'task_name': 'Deploy API to Production Cluster', 'notes': 'Ensure environment secrets are configured', 'status': 'done'}"

initial_state = {
    "messages": [],
    "json_string": raw_json_input,
    "parsed_data": {},
    "current_iteration": 0,
    "max_iterations": 3
}

print("Running deepseek-r1 locally via Ollama and LangGraph...")
for event in app.stream(initial_state):
    print(event)
