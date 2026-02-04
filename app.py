import streamlit as st
import os
import requests
from agents import graph

# Page Config
st.set_page_config(page_title="Multi-Agent Content Factory", page_icon="🤖", layout="wide")

# Custom CSS for aesthetic
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
    }
    .reportview-container {
        background: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏭 LangChain Multi-Agent Content Factory")
st.markdown("Powered by **LangGraph**, **Ollama**, and **DuckDuckGo**.")

# Sidebar: Configuration
st.sidebar.header("⚙️ Configuration")
with st.sidebar:
    st.subheader("Ollama Settings")
    ollama_base_url = st.text_input("Base URL", value="http://localhost:11434")
    model_name = st.text_input("Model Name", value="deepseek-r1:8b")
    
    if st.button("Verify Connection"):
        try:
            response = requests.get(ollama_base_url)
            if response.status_code == 200:
                st.success("✅ Connected to Ollama")
            else:
                st.warning(f"⚠️ Status Code: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Connection Failed: {e}")

    st.markdown("---")
    st.info("Ensure running: `ollama run llama3.2`")

# Main Interface
col1, col2 = st.columns([1, 2])

with col1:
    st.image("https://python.langchain.com/img/favicon.ico", width=50) # Placeholder logo
    st.write("### Workflow")
    st.markdown("""
    1. **Researcher**: Scours the web for facts.
    2. **Writer**: Drafts the content.
    3. **Critic**: Reviews and requests edits.
    """)

with col2:
    topic = st.text_input("Enter Topic", placeholder="e.g., The Future of AI Agents")
    start_btn = st.button("🚀 Launch Agents", type="primary")

if start_btn and topic:
    status_container = st.empty()
    status_container.info("Initializing workflow...")
    
    # We could update environment variables if our agents.py read them dynamically
    # os.environ["OLLAMA_HOST"] = ollama_base_url
    
    try:
        final_state = graph.invoke({"topic": topic, "revision_count": 0})
        
        status_container.success("Workflow Finished!")
        
        st.divider()
        st.subheader("📝 Final Blog Post")
        st.markdown(final_state.get("draft", "No content generated."))
        
        st.divider()
        st.subheader("🔍 Observability Data")
        
        with st.expander("Show Research Data"):
            st.json(final_state.get("research_data", "No data"))
            
        with st.expander("Show Critique History"):
             st.write(final_state.get("critique", "No critique"))

    except Exception as e:
        status_container.error(f"Error executing graph: {e}")
else:
    if start_btn:
        st.warning("Please enter a topic to proceed.")
