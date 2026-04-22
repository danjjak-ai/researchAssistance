import sys
import os
sys.path.append(os.getcwd())

from src.core.llm import get_llm
from src.config import settings

def test_ollama_connection():
    print(f"Testing Ollama Connection...")
    print(f"Provider: {settings.LLM_PROVIDER}")
    print(f"Base URL: {settings.OLLAMA_BASE_URL}")
    print(f"Model: {settings.OLLAMA_MODEL}")
    
    try:
        llm = get_llm()
        response = llm.invoke("Hello, are you working?")
        print("\nSuccess! Response from Ollama:")
        print(response.content)
    except Exception as e:
        print(f"\nFailed to connect to Ollama: {e}")
        print("Please make sure Ollama is running and the model is pulled.")

if __name__ == "__main__":
    test_ollama_connection()
