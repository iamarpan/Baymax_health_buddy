from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementNotVisibleException
chrome_options = Options() 
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)
url = 'https://www.bigbasket.com/cl/bakery-cakes-dairy/'
driver.get(url)  # Replace with the URL of the page you want to scrape
driver.maximize_window()
import pandas as pd
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import re

def scrap_product(links):
    try:
        urls = []
        for link in tqdm(links):
            try:
                partial_id = "thumb"
                driver.get(link)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[contains(@id, '{partial_id}')]")
                ))
                thumbnails = driver.find_elements(By.XPATH,f"//div[contains(@id, '{partial_id}')]")
                for thumbnail in thumbnails:
                    tag = thumbnail.find_elements(By.XPATH,".//img")[1]
                    attr = tag.get_attribute('srcset')
                    final_url = attr.split("?")[0]
                    if final_url:
                        urls.append(final_url+'?tr=w-1080,q=80')
                        print(len(urls))
            except:
                continue

        data = pd.DataFrame({'links':urls})
        data.to_csv('links.csv',mode='a',index=False,header=False)
    except:
        data.to_csv('links.csv',mode='a',index=False,header=False)



def fetchRecords(category_url):
    try:        # Find and click on each product div
        total_pages=70
        links = []
        for i in range(total_pages):
            try:
                url = category_url+'?page='+str(i)
                driver.get(url)
                div_elements = driver.find_elements(By.XPATH,"//li[@class='PaginateItems___StyledLi-sc-1yrbjdr-0 dDBqny']")
                for element in div_elements:
                    tag = element.find_element(By.XPATH,".//a")
                    link = tag.get_attribute('href')
                    links.append(link)
                print(len(links))
            except Exception:
                continue
        return links
    except Exception:
        print("error",Exception)

if __name__ == '__main__':
    category_url = https://www.bigbasket.com/cl/beverages/'
    links = fetchRecords(category_url)
    scrap_product(links)
