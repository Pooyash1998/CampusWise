import os, requests
import time
import csv
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

download_dir = "resources/docs/rwth_pdfs"
def setup_driver():
  options = Options()
  options.add_argument("--headless")
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage") 
  os.makedirs(download_dir, exist_ok=True)

  #options.set_preference("browser.preferences.instantApply", True)
  #options.set_preference("browser.download.useDownloadDir", True)
  #options.set_preference("browser.download.folderList", 2)
  #options.set_preference("browser.download.manager.showWhenStarting", False)
  #options.set_preference("browser.download.dir", os.path.abspath(download_dir))
  #options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
  #options.set_preference("pdfjs.disabled", True)

  return webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

def get_cookies(driver):
    cookies = driver.get_cookies()
    return {cookie["name"]: cookie["value"] for cookie in cookies}

def get_filename_from_headers(response, fallback_filename):
    content_disp = response.headers.get("Content-Disposition")
    if content_disp:
        match = re.search(r'filename\*?=([^;]+)', content_disp, re.IGNORECASE)
        if match:
            filename = match.group(1).strip().strip('"').strip("'")
            return filename
    return fallback_filename

def download_pdf_with_requests(pdf_url, cookies,filenum):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}  # Mimic a real browser
        response = requests.get(pdf_url, cookies=cookies, headers=headers, stream=True)
        response.raise_for_status()
        filename = get_filename_from_headers(response, filenum)
        pdf_path = os.path.join(download_dir, filename)
        with open(pdf_path, "wb") as pdf_file:
            for chunk in response.iter_content(1024):
                pdf_file.write(chunk)
        print(f"Downloaded: {pdf_path}")
    except requests.exceptions.RequestException as e:
        print(f"Download failed for {pdf_url}: {e}")

def scrape_documents():
  driver = setup_driver()
  BASE_URL = "https://www.rwth-aachen.de/cms/root/Die-RWTH/Aktuell/~xhf/Amtliche-Bekanntmachungen/?page=1&showall=1"
  driver.get(BASE_URL)
  driver.implicitly_wait(3)

  li_elements = driver.find_elements(By.XPATH, '//*[@id="main"]/div[4]/ul/li')
  documents = []

  for idx, li in enumerate(li_elements[1:], 1):
    try:
      title = li.find_elements(By.XPATH, './/div[@class="location"]')[0].text.strip()
      pdf_link_tag = li.find_elements(By.XPATH, './/div[@class="location"]/a')
      pdf_url = pdf_link_tag[0].get_attribute("href") if pdf_link_tag else None
      erschienen = li.find_elements(By.XPATH, './/div[@class="location"]')[3].text.strip()
      nummer = li.find_elements(By.XPATH, './/div[@class="location"]')[4].text.strip()
      ordnung = li.find_elements(By.XPATH, './/div[@class="location"]')[5].text.strip()
      auslaufen = li.find_elements(By.XPATH, './/div[@class="location"]')[6].text.strip() if len(li.find_elements(By.XPATH, './/div[@class="location"]')) > 6 else None
      version = None
      if '(' in title and ')' in title:
          year_match = title.split('(')[-1].split(')')[0]
          if '/' in year_match:
              version = year_match.split('/')[-1]
      
      documents.append([idx, title, pdf_url, erschienen, nummer, ordnung, auslaufen, version])
    except Exception as e:
      print(f"Error processing entry {idx}: {e}")

  driver.quit()

  CSV_FILE = "resources/rwth.csv"
  with open(CSV_FILE, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["N", "Title", "PDF URL", "Erschienen", "Nummer", "Ordnung", "Auslaufen","Version"])
    writer.writerows(documents)

  print(f"Saved {len(documents)} documents to {CSV_FILE}")
  return documents

def download_pdfs(documents):
  driver = setup_driver()
  for doc in documents[1:]:
    pdf_url = doc[2]
    if pdf_url:
      print(f"Downloading: {pdf_url}")
      driver.get(pdf_url)
      time.sleep(2)
      cookies = get_cookies(driver)
      filenum = f"{doc[0]}.pdf"
      download_pdf_with_requests(pdf_url, cookies, filenum)
    else:
      print(f"No PDF URL found for: {doc[0]}")
  
  print("All PDFs downloaded successfully!")
  driver.quit()

from openai import OpenAI
import json
from pydantic import BaseModel
from typing import List, Optional

class MetadataSchema(BaseModel):
      degree: Optional[str]
      study_program: Optional[str]
      keywords: List[str]  

def extract_metadata_llm(title, api_key):
    os.environ["OPENAI_API_KEY"]=api_key
    client = OpenAI()
    prompt = f"""
You are an expert metadata extraction assistant. Given the following academic document title, extract the metadata as follows:
- **degree:** (e.g., Bachelor, Master, "Bachelor Lehramt", "Master Lehramt", Staatsexamen Medizin / Zahnmedizin; if not present, use null)
- **study_program:** (e.g., Informatik, Mathematik, etc.; if not present, use null)
- **keywords:** (a list of additional keywords found in the title which are useful for identifying the type of the document like "Prüfungsordnung", "Studienordnung", etc.)
Return your answer strictly as an object with keys "degree", "study_program", and "keywords".
for example for the title "Prüfungsordnung Unterrichtsfach Mathematik, Bachelor, Lehramt an Berufskollegs, (10/2021)" the expected output would be:
 degree='Bachelor Lehramt' study_program='Mathematik' keywords=['Prüfungsordnung', 'Lehramt an Berufskollegs']
Document Title: "{title}"
"""
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert metadata extraction assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format= MetadataSchema

        )
        
        result = response.choices[0].message.parsed
        metadata = result
        return metadata
    except Exception as e:
        print("Error extracting metadata:", e)
        return None

def add_metadata_to_csv(input_csv, output_csv, api_key):
  with open(input_csv, "r", newline="", encoding="utf-8") as infile:
        reader = csv.reader(infile)
        rows = list(reader)
  header = rows[0] + ["Degree", "Study Program", "Keywords"]
  new_rows = [header]
  for row in rows[1:3]:
      title = row[1]
      print(f"Processing title: {title}")
      metadata = extract_metadata_llm(title, api_key)
      if metadata:
          try:
              meta = MetadataSchema.model_dump(metadata)
          except Exception as e:
              print(f"Error parsing metadata JSON for title '{title}': {e}")
              meta = {}
      else:
          meta = {}
      degree = meta.get("degree")
      study_program = meta.get("study_program")
      keywords = meta.get("keywords")
      if isinstance(keywords, list):
        keywords = "; ".join(keywords)
      new_row = row + [degree, study_program, keywords]
      new_rows.append(new_row)
  with open(output_csv, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        writer.writerows(new_rows)

if __name__ == "__main__":
  input_csv = "resources/rwth.csv"
  output_csv = "resources/rwth_with_metadata.csv"
  documents = scrape_documents()
  download_pdfs(documents)
  api_key = os.environ.get("OPENAI_API_KEY")
  add_metadata_to_csv(input_csv, output_csv, api_key)



