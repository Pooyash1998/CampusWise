import streamlit as st

# Set page configuration
st.set_page_config(page_title="CampusWise Chat", layout="centered")

def main():
    st.switch_page("pages/init.py")

if __name__ == "__main__":
  pg = st.navigation([
        st.Page(main),
        st.Page("pages/init.py"),
        st.Page("pages/chat_handler.py", title="💬 Chat", icon="🤖"),
           ], position='hidden')
  pg.run()