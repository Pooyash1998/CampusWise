from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader
import torch
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter

torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)] 

os.environ["TOKENIZERS_PARALLELISM"] = "false"
##### Streamlit clouds sqlite3 is outdated, so we need to use pysqlite3
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
#####
import pandas as pd
from langchain_chroma import Chroma
from utils.donwload_release import download_chromaDB

CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources/chroma")
if not os.path.exists(CHROMA_PATH):
     os.makedirs(CHROMA_PATH)
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-m3",
                                          model_kwargs={"device": "cpu"}, 
                                          show_progress=True, encode_kwargs={"batch_size":32})

def load_and_split():
  #load metadata 
  metadata_df = pd.read_csv("resources/rwth.csv")
  # using "N" as the key
  metadata_dict = {
    row["N"]: {
        "Title" : row["Title"],
        "erschienen": row["Erschienen"],
        "nummer": row["Nummer"],
        "ordnung": row["Ordnung"],
        "version": row["Version"],
        "studiengang": row["Studiengang"],
        "abschlussart": row["AbschlussArt"]
    }
    for _, row in metadata_df.iterrows()
  }
  pdf_dir = "resources/docs/rwth_pdfs"
  documents = []
  doc_counter = 0
  for file in sorted(os.listdir(pdf_dir)):
    if file.endswith(".pdf"):
      file_number = int(file.split("_")[0])
      loader = PyPDFLoader(
              file_path=os.path.join(pdf_dir, file),
      )
      doc_elements = []
      for doc in loader.lazy_load():
        doc_metadata = metadata_dict.get(file_number)
        langchain_doc = Document(
            page_content=doc.page_content,
            metadata={**doc.metadata, **doc_metadata}
        )
        doc_elements.append(langchain_doc)
      documents.extend(doc_elements)
      doc_counter += 1
      print(f"Document {file_number} was loaded. {doc_counter}/{len(os.listdir(pdf_dir))} files")
  print(f"{doc_counter} Documents were loaded")
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
        print("Chroma DB already Exists")
        return Chroma(persist_directory=CHROMA_PATH,embedding_function=embedding_model)
    else:
        download_chromaDB()
        #chunks = load_and_split() not necessary for streamlit
        #return save_to_chroma(chunks)
        return Chroma(persist_directory=CHROMA_PATH,embedding_function=embedding_model)

"""
if __name__ == "__main__":
  get_vectorstore()
"""