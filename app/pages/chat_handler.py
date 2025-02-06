import streamlit as st
from utils.prompt_constructor import construct_promt_and_invoke
from utils.vector_store import get_vectorstore

def chat_page():
  st.title("CampusWise Chat")
  
  # Initialize chat history if it doesn't exist
  if "messages" not in st.session_state:
    st.session_state.messages = []

  # Display chat history
  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  # Chat input
  if prompt := st.chat_input("What would you like to know?"):
    # Display user message
    with st.chat_message("user"):
      st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get response from LLM
    with st.chat_message("assistant"):
      with st.spinner("Thinking..."):
        if "llm" in st.session_state:
          response = construct_promt_and_invoke(st.session_state.llm, prompt)
          st.markdown(response)
          # Add assistant response to chat history
          st.session_state.messages.append({"role": "assistant", "content": response})
        else:
          st.error("LLM model not initialized. Please complete the setup first.")

chat_page()