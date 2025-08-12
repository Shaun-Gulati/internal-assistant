import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
        self.embedding_model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
        
        # Check if API key is properly configured
        if self.api_key and self.api_key != 'your_openai_api_key_here':
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized successfully")
            except ImportError:
                logger.error("OpenAI package not installed. Run: pip install openai")
                self.client = None
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            logger.warning("OpenAI API key not configured. Set OPENAI_API_KEY in your .env file")
            self.client = None
    
    def generate_response(self, message: str, context_docs: List[Dict], user_role: str) -> str:
        """Generate a response using the LLM with RAG context."""
        try:
            if not self.client:
                return "I'm sorry, but I'm not properly configured to respond right now. Please configure your OpenAI API key in the .env file."
            
            # Build context from relevant documents
            context = self._build_context(context_docs)
            
            # Create system prompt based on user role
            system_prompt = self._create_system_prompt(user_role)
            
            # Build the full prompt
            full_prompt = f"{system_prompt}\n\nContext:\n{context}\n\nUser Question: {message}\n\nAnswer:"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {message}"}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"LLM response generation error: {e}")
            return "I'm sorry, but I encountered an error while processing your request."
    
    def _build_context(self, context_docs: List[Dict]) -> str:
        """Build context string from relevant documents."""
        if not context_docs:
            return "No relevant context found."
        
        context_parts = []
        for i, doc in enumerate(context_docs[:5], 1):  # Limit to top 5 docs
            source = doc.get('source', 'Unknown')
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            
            context_part = f"{i}. Source: {source}"
            if metadata.get('channel'):
                context_part += f" (Channel: {metadata['channel']})"
            if metadata.get('author'):
                context_part += f" (Author: {metadata['author']})"
            if metadata.get('timestamp'):
                context_part += f" (Time: {metadata['timestamp']})"
            
            context_part += f"\nContent: {content}\n"
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _create_system_prompt(self, user_role: str) -> str:
        """Create a system prompt tailored to the user's role."""
        base_prompt = """You are an internal AI assistant that helps users find and understand information from their organization's data sources (Slack, GitHub, and Outlook).

You should:
- Provide helpful, accurate responses based on the context provided
- Be concise but informative
- If you don't have enough context, say so rather than making things up
- Focus on the most relevant information for the user's question
- Consider the user's role when providing context and recommendations"""

        role_specific_prompts = {
            'developer': "As a developer, focus on technical details, code changes, and engineering-related information.",
            'marketing': "As a marketing team member, focus on customer feedback, campaign information, and market-related data.",
            'sales': "As a sales team member, focus on customer interactions, leads, and sales-related information.",
            'admin': "As an admin, you have access to all information. Provide comprehensive overviews when appropriate."
        }
        
        role_prompt = role_specific_prompts.get(user_role, "")
        
        return f"{base_prompt}\n\n{role_prompt}"
    
    def get_embeddings(self, text: str) -> List[float]:
        """Get embeddings for a text string."""
        try:
            if not self.client:
                logger.warning("Cannot generate embeddings: OpenAI client not initialized")
                return []
            
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            return []
