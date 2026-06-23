import os
import sys

# Ensure the root directory is in the Python path so absolute imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import google.generativeai as genai
import chromadb
from src.embedding import CustomGoogleGenerativeAiEmbeddingFunction as GoogleGenerativeAiEmbeddingFunction
from dotenv import load_dotenv

import json
import os
import chromadb
from dotenv import load_dotenv
import google.generativeai as genai
from src.embedding import CustomGoogleGenerativeAiEmbeddingFunction as GoogleGenerativeAiEmbeddingFunction

from src.config import DB_DIR, EMBEDDING_MODEL, LLM_MODEL, COLLECTION_NAME, MAX_HISTORY_TURNS, DISTANCE_THRESHOLD

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "your_gemini_api_key_here":
    genai.configure(api_key=api_key)

def query_rag_pipeline(user_query: str, chat_history: list = None, db_path: str = DB_DIR, k: int = 4) -> dict:
    """Searches the database, detects persona, checks escalation, and queries the LLM returning structured JSON."""
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("GEMINI_API_KEY is not set or is using the default template. Please set it in the .env file.")

    if chat_history is None:
        chat_history = []
        
    client = chromadb.PersistentClient(path=db_path)
    embedding_fn = GoogleGenerativeAiEmbeddingFunction(
        api_key=api_key,
        model_name=EMBEDDING_MODEL
    )

    try:
        collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_fn
        )
    except Exception as e:
        raise RuntimeError("Vector database collection not found. Have you ingested documents yet?") from e

    # Query collection for top k closest results
    results = collection.query(
        query_texts=[user_query],
        n_results=k
    )

    documents = results.get('documents', [[]])[0]
    metadatas = results.get('metadatas', [[]])[0]
    distances = results.get('distances', [[]])[0]

    # Escalation condition: No results or poor confidence
    low_confidence = False
    if not documents or (distances and min(distances) > DISTANCE_THRESHOLD):
        low_confidence = True

    context_blocks = []
    citations = []

    for doc, meta in zip(documents, metadatas):
        source_name = meta.get('source', 'Unknown')
        page_num = meta.get('page', 'Unknown')
        citation_str = f"Source: {source_name}, Page: {page_num}"

        context_blocks.append(f"[{citation_str}]\nContext: {doc}")
        if citation_str not in citations:
            citations.append(citation_str)

    context_payload = "\n\n---\n\n".join(context_blocks) if context_blocks else "No relevant documents found."
    
    # Format chat history for prompt
    history_str = ""
    for msg in chat_history[-MAX_HISTORY_TURNS:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_str += f"{role}: {msg['content']}\n"

    system_prompt = f"""You are a Persona-Adaptive Customer Support Agent.
Your job is to read the user's query and chat history, classify the user's persona, provide a helpful response using ONLY the retrieved context, and decide if the conversation must be escalated to a human.

### 1. Persona Detection
Classify the user into exactly one of these personas based on their language and requests:
- "Technical Expert": Uses technical terms, wants logs/details/RCAs.
- "Frustrated User": Emotional language, urgent, repeated complaints.
- "Business Executive": Outcome-focused, concise, wants business impact.
- "Standard User": If none of the above perfectly fit.

### 2. Adaptive Response Generation
Adapt your tone to the detected persona:
- Technical Expert: Detailed, technical, step-by-step, root cause analysis.
- Frustrated User: Empathetic, simple, reassuring, action-oriented.
- Business Executive: Concise, impact-focused, minimal jargon, estimated resolution guidance.
- Standard User: Polite, helpful, clear.

### 3. Escalation Logic
You MUST set `escalation_required = true` if ANY of the following apply:
1. Low confidence or no relevant information is found in the context (Low Confidence Flag: {low_confidence}).
2. The user remains dissatisfied or repeats complaints.
3. The query involves billing, legal, or account-sensitive issues.
4. The issue cannot be resolved using the provided context.

If escalated, provide a structured `handoff_summary`. If NOT escalated, `handoff_summary` must be null.

You MUST respond strictly in valid JSON format matching this structure:
{{
  "persona": "string (Detected Persona)",
  "escalation_required": boolean,
  "handoff_summary": {{
    "persona": "string",
    "issue": "string (Summary of user issue)",
    "documents_used": ["list of strings (filenames)"],
    "attempted_steps": ["list of strings (actions attempted based on history)"],
    "recommendation": "string (Suggested next steps for human agent)"
  }} | null,
  "response": "string (Your adaptive response grounded ONLY in context, cite sources inline like [Source: X, Page: Y])"
}}

Do not include markdown codeblocks around the JSON. Return raw JSON.
"""

    prompt = (
        f"### CHAT HISTORY:\n{history_str}\n\n"
        f"### RETRIEVED CONTEXT:\n{context_payload}\n\n"
        f"### CURRENT USER QUESTION:\n{user_query}\n"
    )

    # Call Gemini to generate the structured JSON answer
    model = genai.GenerativeModel(LLM_MODEL)
    
    try:
        response = model.generate_content(
            contents=[
                {"role": "user", "parts": [system_prompt]},
                {"role": "model", "parts": ["Acknowledged. I will output strictly valid JSON matching the requested schema."]},
                {"role": "user", "parts": [prompt]}
            ],
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )
        
        # Parse JSON
        result_json = json.loads(response.text)
        
        return {
            "answer": result_json.get("response", "Error generating response."),
            "citations": citations,
            "persona": result_json.get("persona", "Standard User"),
            "escalated": result_json.get("escalation_required", False),
            "handoff_summary": result_json.get("handoff_summary"),
            "raw_context": documents
        }
    except Exception as e:
        print(f"Failed to generate or parse JSON: {e}")
        # Fallback
        return {
            "answer": "I apologize, but I encountered an error processing your request. Escalating to a human agent.",
            "citations": [],
            "persona": "Unknown",
            "escalated": True,
            "handoff_summary": {
                "persona": "Unknown",
                "issue": user_query,
                "documents_used": citations,
                "attempted_steps": [],
                "recommendation": "System error during response generation."
            },
            "raw_context": documents
        }

if __name__ == "__main__":
    q = input("Enter your question: ")
    res = query_rag_pipeline(q)
    print("\n--- Answer ---")
    print(res["answer"])
    print(f"\nPersona: {res['persona']} | Escalated: {res['escalated']}")

