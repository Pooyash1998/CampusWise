from langchain_community.chat_models import ChatOpenAI
from langchain_ollama import ChatOllama

def get_llm(use_ollama: bool, api_key: str = None):
    if use_ollama:
        return ChatOllama(model="deepseek-r1:8b")
    else:
        if not api_key:
            raise ValueError("OpenAI API key required when not using Ollama")
        return ChatOpenAI(api_key=api_key,model="gpt-4o")