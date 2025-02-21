import os, requests
import time
import csv
import re
import pandas as pd
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
    return f"{fallback_filename}.pdf"

def download_pdf_with_requests(pdf_url, cookies, id):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(pdf_url, cookies=cookies, headers=headers, stream=True)
        response.raise_for_status()
        filename = get_filename_from_headers(response, id)
        pdf_path = os.path.join(download_dir, f"{id}_{filename}")
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
      
      documents.append([idx, title, pdf_url, erschienen, nummer, ordnung, auslaufen, version, "", ""])
    except Exception as e:
      print(f"Error processing entry {idx}: {e}")

  driver.quit()

  CSV_FILE = "resources/rwth.csv"
  with open(CSV_FILE, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["N", "Title", "PDF URL", "Erschienen", "Nummer", "Ordnung", "Auslaufen","Version","Studiengang","AbschlussArt"])
    writer.writerows(documents)

  print(f"Saved {len(documents)} documents to {CSV_FILE}")
  return documents

def fetch_major(major_list, output_csv):
  driver = setup_driver()
  BASE_URL = "https://www.rwth-aachen.de/cms/root/Die-RWTH/Aktuell/~xhf/Amtliche-Bekanntmachungen/?page=1&showall=1"
  driver.get(BASE_URL)
  driver.implicitly_wait(2)
  
  try:
    cookie_banner = driver.find_element(By.ID, "rwth-cb")
    close_button = cookie_banner.find_element(By.XPATH, '//*[@id="accept-rwth-cb"]')
    close_button.click()
    time.sleep(1)
    print("Cookie banner dismissed")
  except Exception as e:
    driver.execute_script("window.scrollBy(0, 500);")
    print("No cookie banner found")
  
  df = pd.read_csv(major_list, header=0)
  majors = df['Studienfach'].tolist()
  for major in majors:
      driver.get(BASE_URL)
      driver.implicitly_wait(30)
      driver.execute_script("window.scrollBy(0, 900);")
      driver.find_element(By.XPATH,'//*[@id="filterdate"]/div[4]/div/fieldset/span[6]').click()
  
      filter_boxes = driver.find_elements(By.CSS_SELECTOR, "div.filter-box")
      for box in filter_boxes:
        heading = box.find_element(By.TAG_NAME, "h3")
        if heading.text.strip() == "Studienfach":
          # Locate all filter tags
          form_rows = box.find_elements(By.CSS_SELECTOR, "span.form-row")
          for row in form_rows:
            label_element = row.find_element(By.TAG_NAME, "label")
            if label_element.text.strip() == major:
              input_id = label_element.get_attribute("for")
              print(input_id)
              input_element = driver.find_element(By.ID, input_id)
              driver.execute_script("arguments[0].click();", input_element)
              print(f"Clicked on: {major}")
              time.sleep(20)
              driver.implicitly_wait(20)
              # now check the titles
              li_elements = driver.find_elements(By.XPATH, '//*[@id="main"]/div[4]/ul/li')
              for li in li_elements[1:] :
                title = li.find_elements(By.XPATH, './/div[@class="location"]')[0].text.strip()
                df = pd.read_csv(output_csv)
                # Find matching row by title
                matching_row = df[df['Title'] == title]
                if not matching_row.empty:
                  df['Studiengang'] = df['Studiengang'].astype(str)
                  df.loc[df['Title'] == title, 'Studiengang'] = major
                  df.to_csv(output_csv, index=False)
                  print(f"Updated Studiengang to {major} for title: {title}")
              break
          break
  driver.quit()

def fetch_type(output_csv):
  driver = setup_driver()
  BASE_URL = "https://www.rwth-aachen.de/cms/root/Die-RWTH/Aktuell/~xhf/Amtliche-Bekanntmachungen/?page=1&showall=1"
  driver.get(BASE_URL)
  driver.implicitly_wait(2)
  
  try:
    cookie_banner = driver.find_element(By.ID, "rwth-cb")
    close_button = cookie_banner.find_element(By.XPATH, '//*[@id="accept-rwth-cb"]')
    close_button.click()
    time.sleep(1)
    print("Cookie banner dismissed")
  except Exception as e:
    driver.execute_script("window.scrollBy(0, 500);")
    print("No cookie banner found")
    
  for deg_type in ["Bachelor","Master","Lehramt","Staatsexamen Medizin / Zahnmedizin"]:
      driver.get(BASE_URL)
      driver.implicitly_wait(30)
      driver.execute_script("window.scrollBy(0, 900);")
      driver.find_element(By.XPATH,'//*[@id="filterdate"]/div[5]/div/fieldset/span[6]').click()
  
      filter_boxes = driver.find_elements(By.CSS_SELECTOR, "div.filter-box")
      for box in filter_boxes:
        heading = box.find_element(By.TAG_NAME, "h3")
        if heading.text.strip() == "Abschluss":
          # Locate all filter tags
          form_rows = box.find_elements(By.CSS_SELECTOR, "span.form-row")
          for row in form_rows:
            label_element = row.find_element(By.TAG_NAME, "label")
            if label_element.text.strip() == deg_type:
              input_id = label_element.get_attribute("for")
              print(input_id)
              input_element = driver.find_element(By.ID, input_id)
              driver.execute_script("arguments[0].click();", input_element)
              print(f"Clicked on: {deg_type}")
              time.sleep(20)
              driver.implicitly_wait(20)
              # now check the titles
              li_elements = driver.find_elements(By.XPATH, '//*[@id="main"]/div[4]/ul/li')
              for li in li_elements[1:] :
                title = li.find_elements(By.XPATH, './/div[@class="location"]')[0].text.strip()
                df = pd.read_csv(output_csv)
                # Find matching row by title
                matching_row = df[df['Title'] == title]
                if not matching_row.empty:
                  df['AbschlussArt'] = df['AbschlussArt'].astype(str)
                  df.loc[df['Title'] == title, 'AbschlussArt'] = deg_type
                  df.to_csv(output_csv, index=False)
                  print(f"Updated Abschlussart to {deg_type} for title: {title}")
              break
          break
  driver.quit()

def download_pdfs(documents):
  driver = setup_driver()
  for doc in documents[0:]:
    pdf_url = doc[2]
    if pdf_url:
      print(f"Downloading: {pdf_url}")
      driver.get(pdf_url)
      time.sleep(2)
      cookies = get_cookies(driver)
      download_pdf_with_requests(pdf_url, cookies, doc[0])
    else:
      print(f"No PDF URL found for: {doc[0]}")
  
  print("All PDFs downloaded successfully!")
  driver.quit()


if __name__ == "__main__":
  major_list_csv = "resources/major_list.csv"
  output_csv = "resources/rwth.csv"
  #documents = scrape_documents()
  #download_pdfs(documents)
  #fetch_major(major_list_csv,output_csv)
  fetch_type(output_csv)



