import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

global property_prices
global property_addresses
global property_links

URL_ZILLOW = "https://www.zillow.com/san-francisco-ca/rentals/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22map" \
             "Bounds%22%3A%7B%22north%22%3A37.88497916322538%2C%22east%22%3A-122.30527011279297%2C%22south%22%3A37.66" \
             "5441766568215%2C%22west%22%3A-122.56138888720703%7D%2C%22mapZoom%22%3A12%2C%22isMapVisible%22%3Atrue%2C" \
             "%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A872627%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%2C%22f" \
             "ore%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A3000%7D%2C%22auc%22%3A%7B%22value%22%3Af" \
             "alse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsbo%22%3A%7B" \
             "%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7" \
             "D%7D%2C%22isListVisible%22%3Atrue%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A20330%2C%22regionTyp" \
             "e%22%3A6%7D%5D%7D"
URL_GOOGLE_FORM = "https://docs.google.com/forms/d/e/1FAIpQLScv801dlFCnug364CxRhUcHuV5co7B1n1_qwSaOLiF9TKTdiQ/viewfor" \
                  "m?usp=sf_link"

options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(options=options)


def get_zillow_data():
    global property_prices
    global property_addresses
    global property_links
    driver.get(URL_ZILLOW)

    try:
        """Handling the Captcha if it happens"""
        h5 = driver.find_element(By.CSS_SELECTOR, "h5")
        while h5.text == "Please verify you're a human to continue.":
            button = driver.find_element(By.ID, "px-captcha")
            action = ActionChains(driver)
            action.click_and_hold(on_element=button)
            action.perform()
            time.sleep(5)
            action.release()
            time.sleep(1)
    except Exception as exp:
        print(exp)

    driver.implicitly_wait(3)
    time.sleep(1)
    zillow_website = driver.page_source
    soup = BeautifulSoup(zillow_website, "html.parser")
    spans = soup.find_all("span")
    property_prices = [price.text.replace("+ 1 bd", "") for price in spans if price.get("data-test") ==
                       "property-card-price"]
    property_addresses = [address.text for address in soup.find_all("address")]
    a = soup.find_all("a")
    property_links = [f"https://www.zillow.com/{link.get('href')}" for link in a if link.get("data-test") ==
                      "property-card-link"]
    property_links = list(dict.fromkeys(property_links))


def send_data_to_google_form():
    driver.get(URL_GOOGLE_FORM)
    driver.implicitly_wait(5)
    time.sleep(2)

    for itemIndex in range(len(property_links)):
        inputs = [inp for inp in driver.find_elements(By.CSS_SELECTOR, "input") if inp.get_attribute("type") == "text"]
        address_input = inputs[0]
        price_input = inputs[1]
        link_input = inputs[2]
        send_button = [button for button in driver.find_elements(By.CSS_SELECTOR, "div div span span") if button.text ==
                       "Enviar"]
        address_input.send_keys(property_addresses[itemIndex])
        price_input.send_keys(property_prices[itemIndex])
        link_input.send_keys(property_links[itemIndex])
        send_button[0].click()
        driver.get(URL_GOOGLE_FORM)
        driver.implicitly_wait(5)
        time.sleep(2)


get_zillow_data()
send_data_to_google_form()
