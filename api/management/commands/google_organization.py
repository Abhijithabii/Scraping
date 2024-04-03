from django.core.management.base import BaseCommand
from pprint import pprint
import json
import datetime
import os
import pandas as pd
from selenium.webdriver.common.by import By
 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import re
from api.db_utils import get_db
 
 
class Command(BaseCommand):
    help = "Update invalid Document"
 
    def handle(self, *args, **options):
        service = Service(
            executable_path=ChromeDriverManager(chrome_type="google-chrome").install()
        )
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        # options.add_argument('--headless')
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-automation")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-breakpad")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-component-extensions-with-background-pages")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-domain-reliability")
        # options.add_argument("--disable-features=site-per-process")
        options.add_argument("--disable-hang-monitor")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-prompt-on-repost")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-web-resources")
        options.add_argument("--disable-web-security")
        options.add_argument("--force-fieldtrials=SiteIsolationExtensions/Control")
        options.add_argument("--metrics-recording-only")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--no-first-run")
        options.add_argument("--no-sandbox")
        options.add_argument("--password-store=basic")
        options.add_argument("--use-mock-keychain")
        options.add_argument("--safebrowsing-disable-auto-update")
        options.add_argument("--enable-automation")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
 
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 5)
        # Base url
        BASE_URL = "https://www.google.com/maps"
 
        BASE_APP_URL = os.getenv("BASE_APP_URL")
        BASE_SEARCH_SPECIALITY = os.getenv("BASE_SEARCH_SPECIALITY")
        PROJECT_NAME = os.getenv("PROJECT_NAME")
 
        db = get_db()
        collection = db[f"{BASE_SEARCH_SPECIALITY}_organization"]
 
        file_path = "C:/Users/Abhijith/Desktop/DEEANDLEE/Medzen March Development/Python-Medzen/Towns and Cities in UK/towns_and_cities_in_uk.json"
        # file_path = "/home_/ketchupbrightbearcow/MedzenApplication/medzen_react_backend/towns_and_cities_in_uk.json"
 
        with open(file_path, "r") as file:
            data = json.load(file)
        total_result = []
        start_time = datetime.datetime.now()
        for count, search_query in enumerate(data, start=1):
            print(
                "^^^^^^^^^^^^^^^^^^^^^^^^^^^count of input search^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ :",
                count,
                search_query,
            )
            driver.refresh()    
            driver.get(BASE_URL)
            try:
                cookies_div = driver.find_element(By.CLASS_NAME, "G4njw")
                cookies_button = cookies_div.find_element(
                    By.XPATH,
                    "//button[contains(@class,'VfPpkd-LgbsSe') and contains(@aria-label,'Alle akzeptieren')]",
                )
                cookies_button.click()
                print("cookies clicked")
            except:
 
                cookies_button = None
            try:
                form = driver.find_element(By.XPATH, "//form[@id='XmI62e']")
                input_field = form.find_element(
                    By.XPATH, "//input[@id='searchboxinput']"
                )
                input_field.clear()
                input_field.send_keys(f"{BASE_SEARCH_SPECIALITY}, {search_query}")
            except:
                print("Input not found")
            try:
                search_div = driver.find_element(By.XPATH, "//div[@class='pzfvzf']")
                new_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='pzfvzf']"))
                )
                search_button = search_div.find_element(By.ID, "searchbox-searchbutton")
                search_button.click()
            except:
                print("Search button not found")
            try:
                search_result = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "IFMGgb"))
                )
                print("search result found")
            except:
                search_result = None
            try:
                search_result_div = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "k7jAl.lJ3Kh.miFGmb.w6Uhzf")
                    )
                )
            except:
                search_result_div = None
            try:
                check_result = search_result_div.find_element(
                    By.CLASS_NAME, "m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd"
                )
            except:
                check_result = None
 
            try:
                direct_result = WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located(
                            (By.CLASS_NAME, "DUwDvf.lfPIob")
                        )
                    )
            except:
                direct_result = None
           
            # try:
            #     current_url = driver.current_url
            # except:
            #     current_url = None
               
 
            if search_result or check_result:
                target_element_xpath = (
                    '//span[contains(text(), "You\'ve reached the end of the list.")]'
                )
                try:
                    check_end = driver.find_elements(By.XPATH, target_element_xpath)
                except:
                    check_end = None
 
                new_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "k7jAl.lJ3Kh.miFGmb.w6Uhzf")
                    )
                )
                if not check_end:
                    while True:
                        # Scroll down using Keys.PAGE_DOWN
                        driver.find_element(By.CLASS_NAME, "hfpxzc").send_keys(
                            Keys.PAGE_DOWN
                        )
 
                        # Wait for a short time to let the page load
                        driver.implicitly_wait(1)
                        print("scrolling...")
                        # Check if the target element is present
                        if driver.find_elements(By.XPATH, target_element_xpath):
                            print("Target element found. Stopping scrolling.")
                            break
 
                try:
                    new_element = wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, "hfpxzc"))
                    )
                    result_div = driver.find_elements(By.CLASS_NAME, "hfpxzc")
                    print(len(result_div))
                except:
                    result_div = None
 
                for i in result_div:
                    output_data = {}
                   
                    try:
                        name_element = i.find_element(
                            By.XPATH,
                            './following-sibling::div[contains(@class, "bfdHYd") and contains(@class, "Ppzolf") and contains(@class, "OFBs3e")]',
                        )
                        get_name = name_element.find_element(
                            By.CLASS_NAME, "qBF1Pd.fontHeadlineSmall"
                        )
                        name = get_name.text.strip()
                        output_data["name"] = name
                        output_data["location"] = search_query
                        print("Name: ", name)
                    except:
                        name = None
                        print("name not found")
                    try:
                        a_tag = i.find_element(By.XPATH, f"//a[contains(@class, 'hfpxzc') and contains(@aria-label, '{name}')]")
                        scraping_url = a_tag.get_attribute("href")
                        output_data["url"] = scraping_url
                           
                    except:
                        scraping_url = None
                    try:
                        output_data["timestamp"] = datetime.datetime.now()
                        existing = collection.find_one({"name":name})    
                        if existing:
                            # Update existing document
                            collection.update_one({"name": name}, {"$set": output_data})
                        else:
                            # Insert new document
                            collection.insert_one(output_data)
                    except:
                        print("error in inserting")
                   
            elif direct_result:
                try:
                    output_data = {}
                    name_element = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located(
                            (By.CLASS_NAME, "DUwDvf.lfPIob")
                        )
                    )
                    name = name_element.text.strip()
                    output_data["name"] = name
                    output_data["location"] = search_query
                    output_data["url"] = driver.current_url
 
                    # output_data["current_url"] = current_url
                    output_data["timestamp"] = datetime.datetime.now()
                    print("Name: ", name)
                    if existing:
                        # Update existing document
                        collection.update_one({"name": name}, {"$set": output_data})
                    else:
                        # Insert new document
                        collection.insert_one(output_data)
                    # total_result.append(output_data)
                except:
                    print("name not found")
            else:
                continue
       
        end_time = datetime.datetime.now()
        # df = pd.DataFrame(total_result)
        # download_folder_final = (
        #     "C:/Users/deeandlee/Desktop/Medzen Application New/Excel Files"
        # )
        # filename_excel = os.path.join(
        #     download_folder_final, f"{BASE_SEARCH_SPECIALITY}_Organization.xlsx"
        # )
        # df.to_excel(filename_excel, index=False)
 
        self.stdout.write(
            self.style.WARNING(f"START TIME: {start_time}, END TIME: {end_time}")
        )
        self.stdout.write(self.style.SUCCESS("Scraping completed!"))