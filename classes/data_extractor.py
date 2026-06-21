import os
import re
import yaml
import logging
import json
from classes.chroma_database import ChromaDatabase
from classes.chat_manager import AgentLogHandler
from classes.model_utils import ModelUtils
from typing import TypedDict, Dict, Any, List, Optional
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

""" Why the load_agent_skill function? If the skills are in the .agents folder
won't they be found anyways?

You are completely correct about how platform-native tools work, but there is a
major catch when you are building a custom runtime from scratch with Ollama and
LangGraph! Platforms like Claude Code, Cursor, or VS Code Copilot have a built-in
"skill host" that constantly monitors folders like .agents/ or .github/skills/.
However, when you write your own pure Python backend using LangGraph, there is
no magic background engine scanning your hard drive unless you explicitly
code it. """

# 1. Define the Global Agent State
class SkillAgentState(TypedDict):
    user_prompt: str             # The raw incoming message/feed
    db_context: str              # Attached reference information
    discovered_skills: Dict[str, Dict[str, Any]] # Inventory of system skills
    selected_skill: Optional[str] # The skill chosen by the router
    final_output: str            # The structured payload response

class DynamicSkillOrchestrator(ChromaDatabase):
  def __init__(self, session, model):
    # 1. Pass the required argument up to the parent class
    super().__init__(session=session)

    self.router_llm = ChatOllama(
      model=model.model,
      temperature=model.temperature,
      num_ctx=model.num_ctx,
      format="json"
    )

    self.executor_llm = ChatOllama(
      model=model.model,
      temperature=model.temperature,
      num_ctx=model.num_ctx,
      format="json"
    )

    self.skills_dir = ModelUtils.resource_path(os.path.join(".agents", "skills"))
    self.skills_inventory = self._discover_all_available_skills()
    self.workflow = self._build_graph()

  def _discover_all_available_skills(self) -> Dict[str, Dict[str, Any]]:
    """Scans the .agents/ folder for any valid SKILL.md specs."""
    catalog = {}
    if not os.path.exists(self.skills_dir):
        return catalog

    for item in os.listdir(self.skills_dir):
      folder_path = os.path.join(self.skills_dir, item)
      skill_path = os.path.join(folder_path, "SKILL.md")

      if os.path.isdir(folder_path) and os.path.exists(skill_path):
        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse frontmatter and body instructions
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if match:
          try:
            frontmatter = yaml.safe_load(match.group(1))
            name = frontmatter.get("name")
            if name:
              catalog[name] = {
                "description": frontmatter.get("description", ""),
                "full_instructions": match.group(2).strip(),
                "folder_path": folder_path
              }
          except yaml.YAMLError:
            continue
    return catalog

  def _discovery_router_node(self, state: SkillAgentState) -> Dict[str, Any]:
    """AI-powered Discovery Phase: Inspects frontmatters to decide which skill fits."""
    skills = state["discovered_skills"]

    if not skills:
        return {"selected_skill": "none"}

    # Build a low-token summary of your capabilities for the LLM to inspect
    skills_summary = ""
    for name, meta in skills.items():
        skills_summary += f"- SKILL_NAME: {name}\n  DESCRIPTION: {meta['description']}\n\n"

    router_prompt = f"""
    You are a routing agent. Your job is to select the single best SKILL_NAME to handle the user request.
    If no skills match perfectly, return "none".

    AVAILABLE SKILLS:
    {skills_summary}

    USER REQUEST:
    {state["user_prompt"]}

    Respond ONLY with this JSON structure:
    {{ "selected_skill": "SKILL_NAME_HERE" }}
    """

    log_handler = AgentLogHandler()
    config = {"callbacks": [log_handler]}
    response = self.router_llm.invoke([("system", "You are an accurate router."), HumanMessage(content=router_prompt)], config=config)
    logging.info(f"Router response: {str(response)}", exc_info=True)

    try:
        # Safely extract selection from structural JSON output
        data = json.loads(response.content)
        return {"selected_skill": data.get("selected_skill", "none")}
    except Exception:
        return {"selected_skill": "none"}

  def _execute_skill_node(self, state: SkillAgentState) -> Dict[str, Any]:
    """Execution Phase: Loads full instructions and supplementary reference documents."""
    skill_name = state["selected_skill"]
    skill_data = state["discovered_skills"][skill_name]

    instructions = skill_data["full_instructions"]
    folder_path = skill_data["folder_path"]

    # Automatically look for supplementary local references if they exist
    ref_context = ""
    references_dir = os.path.join(folder_path, "references")
    if os.path.exists(references_dir):
        for file in os.listdir(references_dir):
            with open(os.path.join(references_dir, file), "r", encoding="utf-8") as f:
                ref_context += f"\n--- Reference File: {file} ---\n{f.read()}\n"

    system_prompt = f"{instructions}\n\n{ref_context}\n\nGLOBAL APP DATABASE CONTEXT:\n{state['db_context']}"

    log_handler = AgentLogHandler()
    config = {"callbacks": [log_handler]}
    response = self.executor_llm.invoke([
        ("system", system_prompt),
        ("user", state["user_prompt"])
    ], config=config)

    return {"final_output": response.content}

  def _fallback_node(self, state: SkillAgentState) -> Dict[str, Any]:
    """Runs if no custom skills match the request."""
    return {"final_output": "I am sorry, but I do not currently have a specialized skill loaded to process that specific request."}

  def _build_graph(self):
    """Compiles the dynamic routing graph."""
    builder = StateGraph(SkillAgentState)

    # Add processing nodes
    builder.add_node("discover_and_route", self._discovery_router_node)
    builder.add_node("execute_skill", self._execute_skill_node)
    builder.add_node("fallback", self._fallback_node)

    # Entrypoint always runs discovery first
    builder.set_entry_point("discover_and_route")

    # Route depending on the string value inside state["selected_skill"]
    def conditional_routing_logic(state: SkillAgentState):
        selection = state["selected_skill"]
        if selection and selection in state["discovered_skills"]:
            return "execute"
        return "fallback"

    builder.add_conditional_edges(
        "discover_and_route",
        conditional_routing_logic,
        {
            "execute": "execute_skill",
            "fallback": "fallback"
        }
    )

    builder.add_edge("execute_skill", END)
    builder.add_edge("fallback", END)

    return builder.compile()

  def run_chat(self, user_prompt: str, db_context: str = "") -> str:
    """Helper to invoke the pipeline state wrapper."""
    initial_state = {
        "user_prompt": user_prompt,
        "db_context": db_context,
        "discovered_skills": self.skills_inventory,
        "selected_skill": None,
        "final_output": ""
    }

    result = self.workflow.invoke(initial_state)
    return result["final_output"]

if __name__ == "__main__":
    # 1. Initialize orchestrator (will scan your local folder automatically)
    orchestrator = DynamicSkillOrchestrator(skills_dir=".agents")

    # 2. Mock incoming context database payload
    mock_schema = "Table: missing_persons_profiles (fields: full_name, age, last_seen_location)"

    # --- TEST 1: Triggering the Missing Persons Extractor Skill ---
    feed_data = '{"incident": "Missing teenager last seen near main street", "name": "Alex Smith", "age": 15}'

    """ print("--- Running Test 1 (Should trigger missing_persons_data_extractor) ---")
    response_1 = orchestrator.run_chat(user_prompt=feed_data, db_context=mock_schema)
    print(response_1) """

    # --- TEST 2: Testing an unrelated prompt (Should hit fallback gracefully) ---
    # unrelated_prompt = "Can you write a poem about code refactoring?"
    unrelated_prompt = "Roll a d20"
    print("\n--- Running Test 2 (Should trigger Fallback) ---")
    response_2 = orchestrator.run_chat(user_prompt=unrelated_prompt)
    print(response_2)


