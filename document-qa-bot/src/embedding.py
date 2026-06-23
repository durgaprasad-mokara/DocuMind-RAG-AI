import google.generativeai as genai
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings

class CustomGoogleGenerativeAiEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=self.api_key)

    def __call__(self, input: Documents) -> Embeddings:
        result = genai.embed_content(
            model=self.model_name,
            content=input,
            task_type="RETRIEVAL_DOCUMENT",
        )
        
        # Depending on the input length, 'embedding' can be a list of lists or just a list
        # Documents is guaranteed to be a List[str] in ChromaDB
        if result.get("embedding") and isinstance(result["embedding"][0], float):
            return [result["embedding"]]
        return result["embedding"]
