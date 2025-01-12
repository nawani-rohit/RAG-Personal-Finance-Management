from openai import OpenAI
from app.core.config import settings
import numpy as np
from typing import List, Dict, Any

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_model = "text-embedding-ada-002"
        self.completion_model = "gpt-3.5-turbo"
        
    def get_embedding(self, text: str) -> List[float]:
        """Generate embeddings for given text using OpenAI's API"""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {str(e)}")
            return []
    
    def get_completion(self, 
                     query: str, 
                     context: List[str], 
                     instruction: str = "Answer the question based on the provided context.") -> str:
        """Get completion from OpenAI based on query and context"""
        try:
            messages = [
                {"role": "system", "content": instruction},
                {"role": "user", "content": f"Context:\n{' '.join(context)}\n\nQuestion: {query}"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.completion_model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting completion: {str(e)}")
            return f"Error processing query: {str(e)}"
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            return float(np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2)))
        except Exception as e:
            print(f"Error calculating similarity: {str(e)}")
            return 0.0

openai_service = OpenAIService()