# Multi-Agent Content Factory Documentation

## 1. Overview
The **Multi-Agent Content Factory** is an intelligent system designed to automate the creation of high-quality, researched blog posts. It orchestrates a team of specialized AI agents—a **Researcher**, a **Writer**, and a **Critic**—to iteratively produce content that is factually accurate, engaging, and SEO-optimized.

The system is built on **LangGraph** for stateful orchestration and interfaces with a local **Ollama** instance (specifically using the `deepseek-r1:8b` model) for privacy and control.

## 2. Functional Description

### Key Roles
1.  **Researcher 🕵️**:
    *   **Goal**: Gather up-to-date information and facts about the user's requested topic.
    *   **Action**: Performs real-time web searches using DuckDuckGo.
    *   **Output**: A concise summary of relevant findings with sources.

2.  **Writer ✍️**:
    *   **Goal**: distinctDraft a comprehensive blog post.
    *   **Action**: Synthesizes the provided research data into a structured article. It considers previous feedback if currently in a revision loop.
    *   **Output**: A markdown-formatted blog post with a title, introduction, body, and conclusion.

3.  **Critic 🧐**:
    *   **Goal**: Ensure quality control.
    *   **Action**: Reviews the draft for factual accuracy, SEO best practices, and tone.
    *   **Output**: Verification status ("APPROVE" or specific feedback).

### User Workflow
1.  User launches the Streamlit UI.
2.  User configures the local LLM settings (URL and Model Name).
3.  User inputs a topic (e.g., "The Future of Quantum Computing").
4.  The system runs autonomously, displaying real-time updates.
5.  The final, polished blog post is displayed along with the research data and critique history.

## 3. Technical Architecture

### Technology Stack
*   **Orchestration**: [LangGraph](https://langchain-ai.github.io/langgraph/) (Stateful multi-agent graph)
*   **LLM Provider**: [Ollama](https://ollama.com/) (Local inference)
    *   **Model**: `deepseek-r1:8b` (configured as default)
*   **Web Search**: [DuckDuckGo Search](https://pypi.org/project/duckduckgo-search/) (Privacy-focused search engine)
*   **Frontend**: [Streamlit](https://streamlit.io/) (Interactive web interface)
*   **Observability**: [LangSmith](https://smith.langchain.com/) (Tracing and debugging)

### State Management (`AgentState`)
The agents share a unified state object passed between nodes:

```python
class AgentState(TypedDict):
    topic: str           # The initial input topic
    research_data: str   # Raw results from the web search
    draft: str           # The current markdown draft of the post
    critique: str        # Feedback from the critic agent
    revision_count: int  # Counter to prevent infinite loops (max 3)
```

### Graph Logic
The workflow is defined as a directed graph:

1.  **Start** -> **Researcher**: fetch data.
2.  **Researcher** -> **Writer**: generate initial draft.
3.  **Writer** -> **Critic**: review draft.
4.  **Condition (`should_continue`)**:
    *   If **Critic** says "APPROVE": -> **End**.
    *   If **Critic** requests changes: -> **Writer** (Loop).
    *   If `revision_count` >= 3: -> **End** (Safety valve).

## 4. Setup & Running

### Prerequisites
*   Python 3.10+
*   Ollama running locally (`ollama serve`)
*   Model pulled: `ollama pull deepseek-r1:8b`

### Installation
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install streamlit langgraph langchain-ollama duckduckgo-search python-dotenv
```

### Execution
```bash
# Run the application
streamlit run app.py
```
