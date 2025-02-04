import streamlit as st
import openai

# Set page configuration
st.set_page_config(page_title="CampusWise Chat", layout="centered")

# Initialize session state for chat history
if "messages" not in st.session_state:
  st.session_state.messages = []

def initialize_chat():
  # Title and description
  st.title("🎓 CampusWise Chat")
  st.markdown("Dein KI-Studienberater")
  st.header("Deine Informationen")
  major = st.text_input("Studiengang")
  degree = st.selectbox("Abschluss", ["Bachelor", "Master", "Promotion"])
  po = st.text_input("Prüfungsordnung (PO)")
  api_key = st.text_input("OpenAI API Key", type="password")

  # Save button
  if st.button("Chat starten"):
    if api_key and major and degree and po:
      openai.api_key = api_key
      st.session_state.user_info = {
        "major": major,
        "degree": degree,
        "po": po
      }
      st.success("Informationen gespeichert! Du kannst jetzt chatten.")
    else:
      st.error("Bitte fülle alle Felder aus.")

  # Main chat interface
  if "user_info" in st.session_state:
    # Display chat messages
    for message in st.session_state.messages:
      with st.chat_message(message["role"]):
        st.write(message["content"])

    # Chat input
    user_input = st.chat_input("Schreibe deine Nachricht hier...")
    if user_input:
      # Add user message to chat
      st.session_state.messages.append({"role": "user", "content": user_input})
      
      try:
        # Get chatbot response
        response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=[
            {"role": "system", "content": f"Du bist ein Studienberater für einen {st.session_state.user_info['degree']}-Studenten im Studiengang {st.session_state.user_info['major']}. Die gültige Prüfungsordnung ist: {st.session_state.user_info['po']}."},
            *st.session_state.messages
          ]
        )
        
        # Add assistant response to chat
        assistant_response = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        
      except Exception as e:
        st.error(f"Fehler: {str(e)}")
  else:
    st.info("Bitte fülle deine Informationen in der Seitenleiste aus, um zu chatten.")

if __name__ == "__main__":
  initialize_chat()