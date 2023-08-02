import time
import threading
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pika
import json

from src.config.env import DRIVER_CONFIG, RABBITMQ_CONFIG



class BamaScraper:
    def __init__(self, webdriver_path):
        self.url = None
        self.webdriver_path = webdriver_path
        self.driver = None

    def setup_driver(self):
        options = Options()
        # options.add_argument("--headless") # Run Chrome without opening a browser window
        options.add_argument("--disable-gpu") # Disable GPU acceleration
        self.driver = webdriver.Chrome(executable_path=self.webdriver_path, options=options)

    def load_page(self, url):
        self.url = url
        self.driver.get(self.url)
        time.sleep(5)

    def scroll_page(self, scroll_limit=2, scroll_pause_time=5):
        scroll_count = 0
        previous_height = self.driver.execute_script("return document.body.scrollHeight")
        while scroll_count < scroll_limit:
            self.driver.find_element_by_tag_name("body").send_keys(Keys.END)
            time.sleep(scroll_pause_time)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == previous_height:
                break
            previous_height = new_height
            scroll_count += 1

    def get_page_source(self):
        return self.driver.page_source

    def parse_page(self, page_source):
        soup = BeautifulSoup(page_source, "html.parser")
        return soup.find_all("div", class_="bama-ad-holder")[:]

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
    
    def scrape_single_page(self, urls_chunk, queue_name):
        self.setup_driver()
        self.load_page(urls_chunk)
        self.scroll_page()
        page_source = self.get_page_source()
        car_records = self.parse_page(page_source)
        titles, years, mileages, models, prices, locations = self.extract_car_data(car_records)
        self.driver.quit()

        # Establish connection to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_CONFIG["rabbitmq_host"]))
        channel = connection.channel()

        # Create RabbitMQ queue using the unique queue_name for this thread
        channel.queue_declare(queue=queue_name)

        data = []
        for title, year, mileage, model, price, location in zip(titles, years, mileages, models, prices, locations):
            item = {
                "Title": title,
                "Year": year,
                "Mileage": mileage,
                "Model": model,
                "Price": price,
                "Location": location
            }
            data.append(item)

            try:
                # Publish item to the corresponding queue for this thread
                channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(item))
                print(f"Published item to queue: {queue_name}")
            except Exception as e:
                print(f"An error occurred: {str(e)}")

        # Close RabbitMQ connection
        connection.close()

    def scrape(self, url_list):
        # Create and start the threads
        thread_pool = []
        for i, urls_chunk in enumerate(url_list):
            queue_name = f"scraped_data_{i}"  # Unique queue name for each thread
            thread = threading.Thread(target=self.scrape_single_page, args=(urls_chunk, queue_name))
            thread_pool.append(thread)
            thread.start()

        # Wait for all threads to finish
        for thread in thread_pool:
            thread.join()


# Usage
url_list = DRIVER_CONFIG["target_url"]
scraper = BamaScraper(DRIVER_CONFIG["local_webdriver_path"])
scraper.scrape(url_list)

