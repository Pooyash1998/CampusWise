import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

def setup_driver():
  options = Options()
  options.add_argument("--headless")
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")

  download_dir = "docs/rwth_pdfs"
  os.makedirs(download_dir, exist_ok=True)

  options.set_preference("browser.preferences.instantApply", True)
  options.set_preference("browser.download.useDownloadDir", True)
  options.set_preference("browser.download.folderList", 2)
  options.set_preference("browser.download.manager.showWhenStarting", False)
  options.set_preference("browser.download.dir", download_dir)
  options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
  options.set_preference("pdfjs.disabled", True)

  return webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

def scrape_documents():
  driver = setup_driver()
  BASE_URL = "https://www.rwth-aachen.de/cms/root/Die-RWTH/Aktuell/~xhf/Amtliche-Bekanntmachungen/?page=1&showall=1"
  driver.get(BASE_URL)
  driver.implicitly_wait(3)

  li_elements = driver.find_elements(By.XPATH, '//*[@id="main"]/div[4]/ul/li')
  documents = []

  for li in li_elements[1:]:
    try:
      title = li.find_elements(By.XPATH, './/div[@class="location"]')[0].text.strip()
      pdf_link_tag = li.find_elements(By.XPATH, './/div[@class="location"]/a')
      pdf_url = pdf_link_tag[0].get_attribute("href") if pdf_link_tag else None
      erschienen = li.find_elements(By.XPATH, './/div[@class="location"]')[3].text.strip()
      nummer = li.find_elements(By.XPATH, './/div[@class="location"]')[4].text.strip()
      ordnung = li.find_elements(By.XPATH, './/div[@class="location"]')[5].text.strip()
      auslaufen = li.find_elements(By.XPATH, './/div[@class="location"]')[6].text.strip() if len(li.find_elements(By.XPATH, './/div[@class="location"]')) > 6 else None
      
      documents.append([title, pdf_url, erschienen, nummer, ordnung, auslaufen])
    except Exception as e:
      print(f"Error processing entry: {e}")

  driver.quit()

  CSV_FILE = "rwth_pdfs.csv"
  with open(CSV_FILE, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "PDF URL", "Erschienen", "Nummer", "Ordnung", "Auslaufen"])
    writer.writerows(documents)

  print(f"Saved {len(documents)} documents to {CSV_FILE}")
  return documents

def download_pdfs(documents):
  driver = setup_driver()
  for doc in documents[1:]:
    pdf_url = doc[1]
    print(pdf_url)
    if pdf_url:
      driver.get(pdf_url)
      time.sleep(100)
      print(f"Downloaded: {pdf_url}")
    else:
      print(f"No PDF URL found for: {doc[0]}")
  
  print("All PDFs downloaded successfully!")
  driver.quit()

def main():
  #documents = scrape_documents()
  with open("rwth_pdfs.csv", "r") as file:
    reader = csv.reader(file)
    documents = list(reader)
  download_pdfs(documents)

if __name__ == "__main__":
  main()
