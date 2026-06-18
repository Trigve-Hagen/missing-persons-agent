import os
import re
import yaml
from typing import TypedDict, Annotated
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END

# Define Agent State
class AgentState(TypedDict):
    incoming_feed: str
    db_context: str
    skill_activated: bool
    final_output: str

# 1. Parse the standard SKILL.md file
def load_agent_skill(skill_path="missing-persons-extractor/SKILL.md"):
    with open(skill_path, "r") as f:
        content = f.read()

    # Extract YAML frontmatter
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if match:
        frontmatter = yaml.safe_load(match.group(1))
        instructions = match.group(2)
        return frontmatter, instructions
    return {}, content

# 2. Node: Discovery Phase (Checks if skill should run)
def discovery_router(state: AgentState):
    frontmatter, _ = load_agent_skill()
    description = frontmatter.get("description", "")

    # Basic keyword match router simulating Progressive Disclosure discovery
    if "missing persons" in state["incoming_feed"].lower() or "incident" in state["incoming_feed"].lower():
        return "activate_skill"
    return "skip"

# 3. Node: Activation & Execution Phase
def execute_skill_node(state: AgentState):
    frontmatter, instructions = load_agent_skill()

    # Read supporting material from references folder if needed
    with open("missing-persons-extractor/references/database_context.txt", "r") as ref:
        db_context = ref.read()

    # Bind Ollama with JSON structured output formatting
    # Recommended models: llama3.1, qwen2.5, or mistral
    llm = ChatOllama(model="llama3.1", temperature=0.1, format="json")

    system_prompt = f"{instructions}\n\nDATABASE SCHEMA CONTEXT:\n{db_context}"
    user_prompt = f"Analyze this incoming feed and generate the output:\n{state['incoming_feed']}"

    messages = [
        ("system", system_prompt),
        ("user", user_prompt)
    ]

    response = llm.invoke(messages)
    return {"final_output": response.content, "skill_activated": True}

# 4. Compile the LangGraph
workflow = StateGraph(AgentState)

workflow.add_node("execute_skill", execute_skill_node)

# Constructing conditional routing based on discovery
workflow.set_conditional_entry_point(
    discovery_router,
    {
        "activate_skill": "execute_skill",
        "skip": END
    }
)
workflow.add_edge("execute_skill", END)
app = workflow.compile()

# Sample mock execution
test_feed = '{"incident": "Missing teenager last seen at park", "name": "Jane Doe", "age": 16}'

result = app.invoke({
    "incoming_feed": test_feed,
    "db_context": "Table: missing_persons_reports (fields: full_name, age, last_seen_location)",
    "skill_activated": False,
    "final_output": ""
})

print(result["final_output"])
