from langchain_openai import ChatOpenAI
#from langchain_ollama import ChatOllama
import os
def get_llm():
    #if use_ollama:
    #    return ChatOllama(model="deepseek-r1:8b")
    #else:
        #if not api_key:
            #raise ValueError("OpenAI API key required when not using Ollama")
        return ChatOpenAI(api_key=os.environ["OPENAI_API_KEY"],model="gpt-4o")