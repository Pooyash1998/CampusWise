from langchain.chat_models import ChatOpenAI
from langchain.llms import Ollama

def get_llm(use_ollama: bool, api_key: str = None):
    if use_ollama:
        return Ollama(model="deepseek-r1:8b")
    else:
        if not api_key:
            raise ValueError("OpenAI API key required when not using Ollama")
        return ChatOpenAI(api_key=api_key,model="gpt-4o")