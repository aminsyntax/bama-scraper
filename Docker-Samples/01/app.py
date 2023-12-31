import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pandas as pd


class BamaScraper:
    def __init__(self, url, webdriver_path):
        self.url = url
        self.webdriver_path = webdriver_path
        self.driver = None

    def setup_driver(self):
        options = Options()
        options.add_argument("--headless") # Run Chrome without opening a browser window
        options.add_argument("--disable-gpu") # Disable GPU acceleration
        self.driver = webdriver.Chrome(executable_path=self.webdriver_path, options=options)



    def load_page(self):
        self.driver.get(self.url)
        time.sleep(5)

    def scroll_page(self, scroll_limit=10, scroll_pause_time=2):
        scroll_count = 0
        while scroll_count < scroll_limit:
            self.driver.find_element_by_tag_name("body").send_keys(Keys.END)
            time.sleep(scroll_pause_time)
            scroll_count += 1

    def get_page_source(self):
        return self.driver.page_source

    def parse_page(self, page_source):
        soup = BeautifulSoup(page_source, "html.parser")
        return soup.find_all("div", class_="bama-ad-holder")[:200]

    def extract_car_data(self, car_records):
        titles = []
        years = []
        mileages = []
        models = []
        prices = []
        locations = []

        for car in car_records:
            title = car.find("p", class_="bama-ad__title").text.strip()

            year_element = car.find("div", class_="bama-ad__detail-row").find_all("span")[0]
            year = year_element.text.strip() if year_element else ""

            mileage = car.find("div", class_="bama-ad__detail-row").find_all("span")[1].text.strip()

            model = car.find("div", class_="bama-ad__detail-row").find_all("span")[2].text.strip()

            price_element = car.find("span", class_=["bama-ad__negotiable-price", "bama-ad__price"])
            price = price_element.text.strip() if price_element else ""

            location_element = car.find("div", class_="bama-ad__address").find("span")
            location = location_element.text.strip() if location_element else ""

            titles.append(title)
            years.append(year)
            mileages.append(mileage)
            models.append(model)
            prices.append(price)
            locations.append(location)

        return titles, years, mileages, models, prices, locations

    def scrape(self):
        self.setup_driver()
        self.load_page()
        self.scroll_page()
        page_source = self.get_page_source()
        car_records = self.parse_page(page_source)
        titles, years, mileages, models, prices, locations = self.extract_car_data(car_records)
        self.driver.quit()

        data = {
            "Title": titles,
            "Year": years,
            "Mileage": mileages,
            "Model": models,
            "Price": prices,
            "Location": locations
        }
        df = pd.DataFrame(data)
        df.to_excel("bama_car_data1.xlsx", index=False)


# Usage
url = "https://bama.ir/car/peugeot-pars"
webdriver_path = "/usr/local/bin/chromedriver" # Add your webdriver path here

scraper = BamaScraper(url, webdriver_path)
scraper.scrape()