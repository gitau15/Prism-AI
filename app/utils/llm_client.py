from typing import Dict, Any
from app.core.config import settings

class LLMClient:
    """Client for interacting with various LLM providers"""
    
    def __init__(self, provider: str = None):
        self.provider = provider or settings.LLM_PROVIDER
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client based on provider"""
        if self.provider == "gemini":
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.client = genai.GenerativeModel('gemini-pro')
            except ImportError:
                self.client = None
        elif self.provider == "glm":
            # Zhipu AI GLM integration would go here
            pass
        elif self.provider == "mistral":
            # Mistral AI integration would go here
            pass
    
    def generate_response(self, prompt: str) -> str:
        """Generate a response from the LLM"""
        if self.provider == "gemini" and self.client:
            try:
                response = self.client.generate_content(prompt)
                return response.text
            except Exception as e:
                return f"Error generating response: {str(e)}"
        else:
            # Placeholder response for other providers or when not configured
            return f"Simulated response from {self.provider} for prompt: {prompt}"
    
    def format_prompt(self, query: str, context: str) -> str:
        """Format the prompt with the query and retrieved context"""
        prompt = f"""
        You are Prism AI, an intelligent assistant designed to answer questions based on provided documents.
        
        Use the following retrieved context to answer the user's question. If the context doesn't contain
        relevant information, politely indicate that you don't have enough information to answer accurately.
        
        Retrieved Context:
        {context}
        
        User Question:
        {query}
        
        Answer:
        """
        return prompt