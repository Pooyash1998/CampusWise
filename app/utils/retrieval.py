from utils.vector_store import get_vectorstore
import time

def get_retriever(session_states):
  try:
    print("Initializing vector store...")
    vectorstore = get_vectorstore()
    if not vectorstore:
      print("Vector store is being created for the first time. This may take a few minutes...")
      while not vectorstore:
        print(".", end="", flush=True)
        time.sleep(1)
        vectorstore = get_vectorstore()
      print("\nVector store initialization complete!")
  except Exception as e:
    print(f"Error initializing vector store: {str(e)}")
    raise
  user_info = session_states.user_info

  base_filter = {
      "$and": [
          {"studiengang": user_info["Studiengang"]},
          {"abschlussart": user_info["AbschlussArt"]}
      ]
  }

  # If a PO is selected, add condition for Version to be in ["", selected PO]
  if user_info.get("Version"):  
      base_filter["$and"].append({"version": {"$in": ["", user_info["Version"]]}})

  retriever = vectorstore.as_retriever(
      search_kwargs={'k': 15, 'filter': base_filter},
      search_type="similarity"
  )
  return retriever
