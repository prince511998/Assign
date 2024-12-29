import time

from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from googletrans import Translator
import os
import requests
# from bs4 import BeautifulSoup
from collections import Counter

# Initialize Selenium WebDriver
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(
    service=webdriver.chrome.service.Service(ChromeDriverManager().install()))  # Initialize Chrome WebDriver
driver.maximize_window()  # Maximize the browser window

try:
    # Step 1: Navigate to El País website
    driver.get("https://elpais.com/")
    driver.maximize_window()

    # Step 2: Ensure the website is in Spanish (assumed default is Spanish)
    homepage_text = driver.find_element(By.TAG_NAME, "body").text
    if "Opinión" in homepage_text:  # Check for a common Spanish word
        print("The website is displayed in Spanish.")
    else:
        print("The website is not in Spanish.")
    # Step 3: Navigate to the Opinion Section
    opinion_section = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Opinión')][1]"))
    )
    opinion_section.click()
    # Step 4: Scrape Articles (First Five)
    articles = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article"))
    )[:5]
    print(articles)
    article_data = []
    translator = Translator()

    for article in articles:
        title_element = article.find_element(By.TAG_NAME, "h2")
        title = title_element.text
        content_link = title_element.find_element(By.TAG_NAME, "a").get_attribute("href")

        # Navigate to the article page to scrape content
        print(content_link)
        driver.get(content_link)
        content = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-dtm-region='articulo_cuerpo']"))
        ).text

        # Check for cover image
        try:
            img_element = driver.find_element(By.XPATH, "//img[@class='_re  a_m-h']")
            img_url = img_element.get_attribute("src")
        except:
            img_url = None

        # Save article data
        article_data.append({"title": title, "content": content, "img_url": img_url})

        # Go back to the Opinion page
        print(article_data)
        # actions = ActionChains(driver)
        # actions.send_keys(Keys.BACKSPACE).perform()
        driver.execute_script("window.history.back();")
        time.sleep(10)



    # Step 5: Download and Save Cover Images
    os.makedirs("article_images", exist_ok=True)
    for i, article in enumerate(article_data):
        if article["img_url"]:
            response = requests.get(article["img_url"])
            with open(f"article_images/article_{i+1}.jpg", "wb") as img_file:
                img_file.write(response.content)

    # Step 6: Translate Article Titles to English
    translated_titles = []
    for article in article_data:
        translated_title = translator.translate(article["title"], src="es", dest="en").text
        translated_titles.append(translated_title)

    # Print Translated Titles
    print("\nTranslated Titles:")
    for title in translated_titles:
        print(title)

    # Step 7: Analyze Translated Headers
    words = " ".join(translated_titles).split()
    word_count = Counter(word.lower() for word in words)
    repeated_words = {word: count for word, count in word_count.items() if count > 2}

    print("\nRepeated Words in Translated Titles:")
    for word, count in repeated_words.items():
        print(f"{word}: {count}")

finally:
    # Close the browser
    driver.quit()
