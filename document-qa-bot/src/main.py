import streamlit as st
import os
import sys

# Ensure the root directory is in the Python path so absolute imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from src.ingest import main as run_ingestion
from src.query import query_rag_pipeline

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Document Q&A Bot", page_icon="📚", layout="centered")

st.title("📚 Document Q&A Bot with RAG")
st.markdown("Ask questions about your private documents. The AI will answer using only the provided context and cite its sources.")

if not api_key or api_key == "your_gemini_api_key_here":
    st.error("⚠️ GEMINI_API_KEY is not configured! Please update your `.env` file with a valid Google Gemini API key.")
    st.stop()

# Sidebar for controls
with st.sidebar:
    st.header("⚙️ Configuration")
    if st.button("🔄 Re-index Documents"):
        with st.spinner("Extracting and embedding documents..."):
            try:
                run_ingestion()
                st.success("Documents successfully indexed!")
            except Exception as e:
                st.error(f"Error indexing documents: {e}")
    
    st.markdown("---")
    st.markdown("""
    **How it works:**
    1. Place PDF/DOCX files in the `data/` folder.
    2. Click 'Re-index Documents' to chunk and embed them into the local vector database.
    3. Type your question below to retrieve context and generate an answer.
    """)

# Main Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("persona") and message["role"] == "user":
            st.caption(f"*(Detected Persona: {message['persona']})*")
        st.markdown(message["content"])
        if message.get("citations"):
            st.caption("Sources: " + ", ".join(message["citations"]))
        if message.get("escalated") and message.get("handoff"):
            st.error("🚨 **ESCALATION REQUIRED** 🚨")
            st.json(message["handoff"])

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Display user prompt
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Searching documents & generating adaptive answer..."):
            try:
                # Pass chat history to the pipeline (exclude the current prompt which was just added)
                chat_history = st.session_state.messages[:-1]
                
                result = query_rag_pipeline(prompt, chat_history=chat_history)
                
                answer = result.get("answer", "Error generating response.")
                citations = result.get("citations", [])
                persona = result.get("persona", "Unknown")
                escalated = result.get("escalated", False)
                handoff = result.get("handoff_summary")
                
                st.session_state.messages[-1]["persona"] = persona
                
                # Display Persona Badge
                st.info(f"**Detected Persona**: {persona}")
                
                # Display Answer
                message_placeholder.markdown(answer)
                
                if citations:
                    st.caption("Sources: " + ", ".join(citations))
                    
                if escalated and handoff:
                    st.error("🚨 **ESCALATION REQUIRED** 🚨")
                    st.warning("Transferring to a human agent. Handoff Summary:")
                    st.json(handoff)
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer,
                    "citations": citations,
                    "persona": persona,
                    "escalated": escalated,
                    "handoff": handoff
                })
            except Exception as e:
                error_msg = f"Error during query: {e}"
                message_placeholder.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
