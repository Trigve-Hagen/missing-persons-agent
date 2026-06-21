import os
import re
from typing import Annotated, TypedDict

# Core LangChain & LangGraph Abstractions
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

# 1. State Definition
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# 2. Vector Store Setup (langchain_chroma)
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vector_store = Chroma(
    collection_name="local_knowledge",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

@tool
def query_knowledge_base(query: str) -> str:
    """Queries the local Chroma vector store for context on specific documents."""
    docs = retriever.invoke(query)
    return "\n\n".join([doc.page_content for doc in docs])

# 3. Dynamic Parser for Official agentskills.io SKILL.md files
def parse_agentskills_io(skills_dir: str = ".agent/skills") -> list:
    """Discovers and parses official agentskills.io specification markdown tools."""
    discovered_tools = []
    if not os.path.exists(skills_dir):
        return discovered_tools

    for item in os.listdir(skills_dir):
        skill_path = os.path.join(skills_dir, item)
        skill_md_path = os.path.join(skill_path, "SKILL.md")

        if os.path.isdir(skill_path) and os.path.exists(skill_md_path):
            with open(skill_md_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract YAML Front Matter Block
            match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
            if match:
                yaml_text, instructions = match.groups()

                # Simple regex extraction for name and description properties
                name_match = re.search(r"^name:\s*(.+)$", yaml_text, re.MULTILINE)
                desc_match = re.search(r"^description:\s*(.+)$", yaml_text, re.MULTILINE)

                if name_match and desc_match:
                    skill_name = name_match.group(1).strip()
                    skill_desc = desc_match.group(1).strip()

                    # Programmatically create a LangChain tool containing the markdown directives
                    def create_tool(name, desc, body, path):
                        @tool(name=name)
                        def dynamic_skill(user_query: str) -> str:
                            # Dynamic invocation loads instructions & maps to execution path
                            return f"Skill System Instructions:\n{body}\n\n[Executed relative path: {path}]"

                        dynamic_skill.description = f"{desc} Argument: user_query context."
                        return dynamic_skill

                    discovered_tools.append(create_tool(skill_name, skill_desc, instructions, skill_path))
                    print(f"📦 Registered agentskills.io layout: {skill_name}")

    return discovered_tools

# 4. Bind Combined Tools (Vector Database + agentskills.io Specifications)
tools = [query_knowledge_base]
tools.extend(parse_agentskills_io())
tool_node = ToolNode(tools)

# 5. Model Bindings
llm = ChatOllama(model="llama3.1:8b", temperature=0).bind_tools(tools)

# 6. Graph Control Flow Architecture
def call_model(state: AgentState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# 7. Thread Execution Loop
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "agentskills_io_2026"}}

    prompt = "Can you launch the server-check workflow to see if our production machine is active?"
    print(f"\nUser: {prompt}")

    for event in app.stream({"messages": [HumanMessage(content=prompt)]}, config, stream_mode="values"):
        event["messages"][-1].pretty_print()
