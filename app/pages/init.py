import streamlit as st
import json
from pathlib import Path
from time import sleep
from llm import get_llm

# Initialize session states
if "messages" not in st.session_state:
  st.session_state.messages = []
if "llm" not in st.session_state:
    st.session_state.llm = None

def load_study_data():
    data_path = Path(__file__).parent.parent / 'resources' / 'study_programs.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"Loaded data structure: {data.keys()}")
        return data

def get_available_pos(data, major, degree):
    if major and degree:
        return data['study_programs'].get(major, {}).get(degree, [])
    return []


st.title("🎓 CampusWise Chat")
st.markdown("Dein KI-Studienberater")
st.header("Deine Informationen")
study_data = load_study_data()
study_programs = list(study_data['study_programs'].keys())
major = st.selectbox("Studiengang", options= study_programs)
degree = st.selectbox("Abschluss", options = ["Bachelor", "Master", "Promotion"])
  
# Only show PO dropdown if both major and degree are selected
available_pos = get_available_pos(study_data, major, degree)
if major and degree and available_pos:
    po = st.selectbox("Prüfungsordnung (PO)", options=available_pos)
else:
    st.text("Bitte wähle erst Studiengang und Abschluss aus")

use_ollama = st.checkbox("Lokales Modell (Ollama) verwenden")
if not use_ollama:
      api_key = st.text_input("OpenAI API Key", type="password")
  
# Save button
if st.button("Chat starten"):
    if major and degree and po :
        try:
            # Initialize LLM
            llm = get_llm(use_ollama, api_key if not use_ollama else None)
            st.session_state.llm = llm
            st.session_state.user_info = {
                "major": major,
                "degree": degree,
                "po": po,
                "use_ollama": use_ollama
            }
            st.success("Informationen gespeichert! Du kannst jetzt chatten.")
            sleep(1)
            st.switch_page("pages/chat_handler.py")
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Fehler beim Initialisieren des LLM: {str(e)}")
    else:
        st.error("Bitte fülle alle Felder aus.")