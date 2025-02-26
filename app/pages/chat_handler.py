import streamlit as st
from utils.prompt_constructor import construct_prompt
from utils.auth import check_authentication
from utils.retrieval import get_retriever
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser

from langchain_community.chat_message_histories import StreamlitChatMessageHistory
check_authentication()

st.title("CampusWise Chat")

# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I help you?")

# Set up the LangChain, passing in Message History
prompt = construct_prompt()
rag_chain = prompt | st.session_state.llm | StrOutputParser()

chain_with_history = RunnableWithMessageHistory(
    rag_chain,
    lambda session_id: msgs,
    input_messages_key="user_input",
    history_messages_key="history",
)
# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

# If user inputs a new prompt, generate and draw a new response
if prompt := st.chat_input():
    st.chat_message("human").write(prompt)
    # new messages are saved to history automatically by Langchain during run
    retrieval_res = get_retriever(st.session_state).invoke(prompt)
    response = chain_with_history.stream({"user_input": prompt,"context":retrieval_res}, config={"configurable": {"session_id": "any"}})
    with st.chat_message("ai"):
        st.write_stream(response)
 