from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self, model_name: str="gemini-2.0-flash")-> None:
        """
        Initialize Gemini client with MCP tool integration.
        
        Args:
            model_name: The Gemini model to use
        """
        self.model = model_name
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY", None),
        )
    
    def __call__(self, prompt: str) -> str:
        """
        Generate content using the Gemini model based on the provided prompt.
        
        Args:
            prompt: The input text to generate content for
        
        Returns:
            The generated content as a string
        """
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            raise e