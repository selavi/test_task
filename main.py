import pickle
import time
from os.path import exists

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_driver():
    options = webdriver.FirefoxOptions()
    options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) "
                                                         "Gecko/20100101 Firefox/107.0")
    options.add_argument("--headless")
    options.set_preference("permissions.default.image", 2)
    return webdriver.Firefox(options=options)


def get_driver(url, wait):
    driver = setup_driver()
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(wait)
    return driver


def get_next_catalog_url():
    current = 0
    while True:
        current += 1
        if current > 1:
            url = f"https://www.ozon.ru/category/smartfony-15502/?page={current}&sorting=rating"
        else:
            url = "https://www.ozon.ru/category/smartfony-15502/?sorting=rating"
        yield url


def get_phones_links(number_of_phones):
    phones_links = []
    try:
        for url in get_next_catalog_url():
            print("Amount collected links ", len(phones_links))
            if len(phones_links) >= number_of_phones:
                break
            driver = get_driver(url, 4)
            print("Parsing this URL: ", url)
            for elem in driver.find_elements(By.XPATH, "//a[@class='tile-hover-target ok9']"):
                if len(phones_links) >= number_of_phones:
                    break
                phones_links.append(elem.get_attribute("href"))
            driver.quit()
    except Exception as ex:
        print(ex)
    finally:
        driver.quit()

    return phones_links


def collect_phone_os_data(list_urls, start):
    try:
        for i, url in enumerate(list_urls[start:]):
            phone_model = os_ver = ''
            driver = get_driver(url, 0)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "section-characteristics")))
            phone_model = driver.find_element(By.TAG_NAME, "h1").text
            for elem in driver.find_elements(By.TAG_NAME, "dd"):
                if elem.text.startswith(("iOS ", "Android ")):
                    os_ver = elem.text
            if not os_ver:
                os_ver = "not present"
            print(f"{i+1+start} Phone model: {phone_model}, os version: {os_ver}")
            with open("parsed_data.txt", "a", encoding="utf-8") as file:
                file.write(f"{phone_model},{os_ver}\n")
            driver.quit()
    except Exception as ex:
        print(ex)
    finally:
        print("Completed")
        driver.quit()


def main():
    if not exists("list_urls"):
        list_urls = get_phones_links(100)
        with open('list_urls', 'wb') as fp:
            pickle.dump(list_urls, fp)
    else:
        with open('list_urls', 'rb') as fp:
            list_urls = pickle.load(fp)

    start = 0
    if exists("parsed_data.txt"):
        with open('parsed_data.txt') as f:
            start = sum(1 for _ in f)

    collect_phone_os_data(list_urls, start)


if __name__ == '__main__':
    main()
