from openai import OpenAI
from app.core.config import settings
import numpy as np
from typing import List, Dict, Any
import time
import logging

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_model = "text-embedding-3-small"  # Updated to newer model
        self.completion_model = "gpt-4-turbo-preview"  # Updated to GPT-4
        self.max_retries = 3
        self.retry_delay = 1
        
    def get_embedding(self, text: str) -> List[float]:
        """Generate embeddings for given text using OpenAI's API with retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = self.client.embeddings.create(
                    model=self.embedding_model,
                    input=text,
                    encoding_format="float"
                )
                return response.data[0].embedding
            except Exception as e:
                logger.warning(f"Embedding attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error(f"All embedding attempts failed: {str(e)}")
                    return []
    
    def get_completion(self, 
                     query: str, 
                     context: List[str], 
                     instruction: str = "Answer the question based on the provided context.",
                     temperature: float = 0.3) -> str:
        """Get completion from OpenAI based on query and context with enhanced prompting"""
        try:
            # Enhanced system prompt for financial analysis
            enhanced_instruction = f"""You are a professional financial analyst assistant. {instruction}

Key guidelines:
- Always provide accurate, factual answers based on the provided context
- If calculations are needed, show your work step by step
- If the context doesn't contain enough information, clearly state what's missing
- Use clear, professional language suitable for financial reporting
- Include relevant numbers and dates when available
- If you're unsure about something, acknowledge the uncertainty

Context information:"""
            
            # Format context for better readability
            formatted_context = "\n\n".join([f"Document excerpt {i+1}:\n{ctx}" for i, ctx in enumerate(context)])
            
            messages = [
                {"role": "system", "content": enhanced_instruction},
                {"role": "user", "content": f"{formatted_context}\n\nQuestion: {query}\n\nPlease provide a comprehensive answer based on the above context."}
            ]
            
            response = self.client.chat.completions.create(
                model=self.completion_model,
                messages=messages,
                temperature=temperature,
                max_tokens=1000,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error getting completion: {str(e)}")
            return f"Error processing query: {str(e)}"
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            if not embedding1 or not embedding2:
                return 0.0
            
            # Convert to numpy arrays for better performance
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            return float(dot_product / (norm1 * norm2))
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def analyze_financial_trends(self, text_content: str) -> Dict[str, Any]:
        """Analyze financial trends in the provided text"""
        try:
            instruction = """Analyze the financial data and provide insights on:
1. Key financial metrics (balances, transactions, etc.)
2. Notable trends or patterns
3. Potential concerns or opportunities
4. Summary of financial health

Format your response as a structured analysis."""
            
            response = self.get_completion(
                query="Analyze this financial data and provide insights",
                context=[text_content],
                instruction=instruction,
                temperature=0.2
            )
            
            return {
                "analysis": response,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Error in financial analysis: {str(e)}")
            return {"error": str(e)}
    
    def extract_financial_entities(self, text: str) -> Dict[str, Any]:
        """Extract financial entities like amounts, dates, account numbers, etc."""
        try:
            instruction = """Extract the following financial entities from the text:
- Monetary amounts (with currency)
- Dates and time periods
- Account numbers or identifiers
- Transaction types
- Financial institutions mentioned

Return the information in a structured format."""
            
            response = self.get_completion(
                query="Extract financial entities from this text",
                context=[text],
                instruction=instruction,
                temperature=0.1
            )
            
            return {
                "entities": response,
                "extraction_time": time.time()
            }
        except Exception as e:
            logger.error(f"Error extracting financial entities: {str(e)}")
            return {"error": str(e)}

openai_service = OpenAIService()