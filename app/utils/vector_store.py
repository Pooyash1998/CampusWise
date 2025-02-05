from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
import os

CHROMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "/docs/chroma/"))
if not os.path.exists(CHROMA_PATH):
     os.makedirs(CHROMA_PATH)
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                          model_kwargs={"device": "cpu"}, 
                                          show_progress=True, encode_kwargs={"batch_size":16})

def load_and_split():
  # Load documents
  loader = PyPDFDirectoryLoader("docs/")
  documents = loader.load()
  
  text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=2000,
      chunk_overlap=200,
      length_function=len,
      add_start_index=True,
  )
  chunks = text_splitter.split_documents(documents)
  return chunks

def save_to_chroma(chunks):
  vectorstore = Chroma.from_documents(
          documents=chunks,
          embedding=embedding_model,
          persist_directory=CHROMA_PATH
        )
  return vectorstore

def get_vectorstore():
    if os.path.exists(os.path.join(CHROMA_PATH, 'chroma.sqlite3')):
        print("Chroma DB with all-MiniLM-L6-v2 already Exists")
        return Chroma(persist_directory=CHROMA_PATH,embedding_function=embedding_model)
    else:
        chunks = load_and_split()
        return save_to_chroma(chunks)
