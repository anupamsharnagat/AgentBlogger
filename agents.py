import os
from dotenv import load_dotenv
import langchain
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from duckduckgo_search import DDGS
from langchain_core.messages import SystemMessage, HumanMessage

# Load env variables
load_dotenv()
langchain.debug = True

# Define the shared state
class AgentState(TypedDict):
    topic: str
    research_data: str
    draft: str
    critique: str
    revision_count: int

# Initialize LLM
llm = ChatOllama(model="deepseek-r1:8b", base_url="http://localhost:11434", temperature=0.7)

# --- Nodes ---

def researcher(state: AgentState):
    """
    Search the web for the topic.
    """
    print(f"--- RESEARCHER: {state['topic']} ---")
    topic = state['topic']
    try:
        # Direct use of DDGS
        results = DDGS().text(f"latest information and facts about {topic}", max_results=5)
        # Format results to string
        search_results = "\n\n".join([f"**{r['title']}**\n{r['body']}\nSource: {r['href']}" for r in results])
    except Exception as e:
        search_results = f"Search failed: {e}"
    
    return {"research_data": search_results, "revision_count": 0}

def writer(state: AgentState):
    """
    Draft markdown blog post using research data.
    """
    print("--- WRITER ---")
    topic = state['topic']
    data = state['research_data']
    critique = state.get('critique', '')
    
    prompt = f"""
    You are a professional blog post writer.
    Topic: {topic}
    Research Data: {data}
    
    Previous Critique (if any): {critique}
    
    Write a comprehensive, engaging markdown blog post about the topic.
    Ensure it incorporates the research data accurately.
    Structure it with a catchy title, introduction, body paragraphs, and conclusion.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"draft": response.content}

def critic(state: AgentState):
    """
    Audit post for SEO and facts.
    """
    print("--- CRITIC ---")
    draft = state['draft']
    
    prompt = f"""
    You are a senior editor and SEO specialist.
    Review the following blog post draft:
    
    {draft}
    
    Check for:
    1. Factual accuracy based on general knowledge.
    2. SEO best practices (keywords, structure).
    3. Engagement and tone.
    
    If the post is good and needs no major changes, reply with "APPROVE".
    If it needs changes, provide specific feedback and recommendations.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"critique": response.content, "revision_count": state.get("revision_count", 0) + 1}

# --- Conditional Logic ---

def should_continue(state: AgentState):
    """
    Decide whether to loop back to writer or end.
    """
    critique = state['critique']
    count = state['revision_count']
    
    if "APPROVE" in critique and "not" not in critique.lower(): # Simple check, can be more robust
        return "end"
    
    if count >= 3: # Max revisions to prevent infinite loops
        print("--- MAX REVISIONS REACHED ---")
        return "end"
        
    return "rewrite"

# --- Graph Construction ---

builder = StateGraph(AgentState)

builder.add_node("researcher", researcher)
builder.add_node("writer", writer)
builder.add_node("critic", critic)

builder.add_edge(START, "researcher")
builder.add_edge("researcher", "writer")
builder.add_edge("writer", "critic")

builder.add_conditional_edges(
    "critic",
    should_continue,
    {
        "rewrite": "writer",
        "end": END
    }
)

graph = builder.compile()
