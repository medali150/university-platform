"""
AI Service for Smart Classroom
Handles Groq AI integration (Ultra-fast LLMs)
"""
import os
from typing import Optional, List
from groq import Groq


def get_groq_client():
    """Get or create Groq client with current API key"""
    api_key = os.getenv("GROQ_API_KEY", "")
    if api_key:
        return Groq(api_key=api_key)
    return None


class GroqAIService:
    """Groq AI service wrapper - Ultra-fast inference"""
    
    @staticmethod
    async def generate_completion(
        prompt: str,
        model: str = "llama-3.3-70b-versatile",  # Groq's latest & fastest model
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Optional[str]:
        """
        Generate text completion using Groq
        
        Available models (2025):
        - llama-3.3-70b-versatile (Recommended - Latest & Best)
        - llama-3.1-8b-instant (Fastest)
        - mixtral-8x7b-32768 (Large context)
        - gemma2-9b-it (Google's Gemma)
        """
        
        groq_client = get_groq_client()
        
        if not groq_client:
            print("❌ Groq API key not configured")
            return None
        
        try:
            response = groq_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            return None
    
    
    @staticmethod
    async def generate_embeddings(text: str, model: str = "text-embedding-ada-002") -> Optional[List[float]]:
        """
        Generate embeddings for text
        Note: Groq doesn't provide embeddings yet, using local alternative
        """
        
        print("ℹ️ Groq doesn't support embeddings yet. Using local TF-IDF vectorization.")
        # Fallback to scikit-learn for embeddings
        from sklearn.feature_extraction.text import TfidfVectorizer
        try:
            vectorizer = TfidfVectorizer(max_features=384)
            vector = vectorizer.fit_transform([text]).toarray()[0]
            return vector.tolist()
        except Exception as e:
            print(f"❌ Error generating embeddings: {e}")
            return None


# Global instance (keeping old name for compatibility)
openai_service = GroqAIService()
groq_service = GroqAIService()
