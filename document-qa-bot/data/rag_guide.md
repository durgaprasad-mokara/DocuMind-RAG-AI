# Retrieval-Augmented Generation (RAG) Explained

Retrieval-Augmented Generation (RAG) is an AI framework that improves the quality of Large Language Model (LLM) generated responses by grounding the model on external sources of knowledge.

## How Full RAG Works
A full RAG system operates in two main phases:
1. **Retrieval**: When a user asks a question, the system searches a Vector Database for the most relevant information. This search uses semantic embeddings to find text chunks that match the intent of the query.
2. **Generation**: The retrieved context is injected into a prompt alongside the original user query. The LLM then generates a final response using *only* the retrieved context, significantly reducing hallucinations and improving factual accuracy.

## Access to RAG in this Document
This document serves as proof that the bot has access to RAG knowledge! The system is utilizing RAG right now to read this exact text and deliver the answer back to the user.
