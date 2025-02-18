import streamlit as st
import os
# Set page configuration
st.set_page_config(page_title="CampusWise Chat", layout="centered")

def main():
  if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

  if not st.session_state.logged_in:
    st.title("Welcome to CampusWise")
    pin = st.text_input("Enter PIN", type="password")
    if pin == st.secrets["MASTER_PASS"]:
      st.session_state.logged_in = True
      os.environ["OPENAI_API_KEY"] == st.secrets["OPENAI_API_KEY"]
      st.switch_page("pages/init.py")
    elif pin:
      st.error("Incorrect PIN")
  else:
    st.switch_page("pages/init.py")

if __name__ == "__main__":
  pg = st.navigation([
    st.Page(main),
    st.Page("pages/init.py"),
    st.Page("pages/chat_handler.py", title="💬 Chat", icon="🤖"),
  ], position='hidden')
  pg.run()