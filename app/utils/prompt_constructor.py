from langchain_core.prompts import ChatPromptTemplate
from utils.vector_store import get_vectorstore
system_message = """
Du bist ein Experte für Studienberatung und deine Aufgabe ist es, komplexe Fragen zu beantworten.
Gehe davon aus, dass sich alle Fragen auf das Studium beziehen.
Halte deine Antworten:
- sachlich und faktenbasiert
- auf die bereitgestellten RAG-Informationen beschränkt
- klar strukturiert und leicht verständlich
- höflich und professionell

Wichtig:
- Erfinde keine Informationen
- Bleibe bei den verfügbaren Fakten
- Gib zu, wenn du etwas nicht weißt
- Verweise bei Unsicherheit auf die offizielle Studienberatung

Format your responses in a clear, easy-to-read structure.
"""
# Define the prompt template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("system", "Retrieved Information from RAG: {retrieved_results}"),
    ("user", "User Input: {user_input}"),
    ("assistant", "Response: ")
])
def perform_rag_retrieval(user_input):
  vectorstore = get_vectorstore()
  retriever = vectorstore.as_retriever(
    search_kwargs={'k': 5}
  )
  results = retriever.invoke(user_input)
  return results
def construct_promt_and_invoke(LLM, user_input):
  chain = prompt_template | LLM 
  rag_retrieval_results = perform_rag_retrieval(user_input)
  response = chain.invoke({"user_input" : user_input, 
                           "retrieved_results" : rag_retrieval_results,})
  return response
  