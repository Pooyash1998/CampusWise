import streamlit as st
import json
from pathlib import Path
from time import sleep
from utils.llm import get_llm
from utils.auth import check_authentication

check_authentication()

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

def get_available_degreeTypes(data, major):
    degrees = (data['study_programs'].get(major, {}))
    if isinstance(degrees, dict):
        return list(degrees.keys())
    return []

def get_available_pos(data, major, degree):
    if major and degree:
        return data['study_programs'].get(major, {}).get(degree, [])
    return []

st.title("🎓 CampusWise Chat")
st.markdown("Dein KI-Studienberater")
st.header("Deine Informationen")
study_data = load_study_data()
studiengang = list(study_data['study_programs'].keys())
major = st.selectbox("Studiengang", options= studiengang, index=22)

# Only show degree dropdown if major is selected
if major:
    available_deg_types = get_available_degreeTypes(study_data,major)
    degree = st.selectbox("AbschlussArt", options=available_deg_types)
else:
    degree = None
    st.text("Bitte wähle erst einen Studiengang aus")
# Only show PO dropdown if both major and degree are selected
available_pos = get_available_pos(study_data, major, degree)
if major and degree and available_pos:
    po = st.selectbox("Prüfungsordnung (PO)", options=available_pos)
else:
    st.text("Bitte wähle erst Studiengang und Abschluss aus")

#use_ollama = st.checkbox("Lokales Modell (Ollama) verwenden")
#if not use_ollama:
#      api_key = st.text_input("OpenAI API Key", type="password")
  
# Save button
if st.button("Chat starten"):
    if major and degree and po :
        try:
            # Initialize LLM
            #llm = get_llm(use_ollama, api_key if not use_ollama else None)
            llm = get_llm()
            st.session_state.llm = llm
            st.session_state.user_info = {
                "Studiengang": major,
                "AbschlussArt": degree,
                "Version": po,
                #"use_ollama": use_ollama
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