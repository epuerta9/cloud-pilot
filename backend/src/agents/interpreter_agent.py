"""Interpreter agent for converting user requests into AWS service specifications."""

from typing import Dict, Optional
from llama_index.llms.openai import OpenAI


class InterpreterAgent:
    """Agent for interpreting user requests into AWS service specifications."""
    
    def __init__(self, model_name: str = "gpt-4"):
        """Initialize the interpreter agent."""
        self.llm = OpenAI(model=model_name)
    
    def interpret_request(self, user_request: str) -> str:
        """
        Convert a user's plain language request into AWS service specifications.
        
        Args:
            user_request: The user's infrastructure request in plain language
            
        Returns:
            A technical specification of required AWS services
        """
        prompt = f"""
        Convert this user's infrastructure request into specific AWS services needed:
        
        User Request: "{user_request}"
        
        Consider:
        1. What AWS services would best fulfill this need
        2. Any supporting services required
        3. Basic configuration needs
        
        Format your response as a technical specification focused only on the AWS services needed.
        Be specific but concise.
        
        Example:
        Input: "I want to store files"
        Output: "Requires an S3 bucket for object storage with appropriate IAM roles for access control"
        
        Return only the technical specification, no explanations.
        """
        
        response = self.llm.complete(prompt)
        return response.text.strip() 