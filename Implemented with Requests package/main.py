import requests
from bs4 import BeautifulSoup
import pandas as pd

# Send a GET request to the URL with headers
url = "https://bama.ir/car/peugeot-pars"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
response = requests.get(url, headers=headers)

# Parse the HTML content
soup = BeautifulSoup(response.text, "html.parser")

# Find all the ad holders on the page
car_records = soup.find_all("div", class_="bama-ad-holder")[:200]

# Create lists to store the scraped data
titles = []
years = []
mileages = []
models = []
prices = []
locations = []

# Iterate over the ad holders and extract the required information
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


# Create a DataFrame from the scraped data
data = {
    "Title": titles,
    "Year": years,
    "Mileage": mileages,
    "Model": models,
    "Price": prices,
    "Location": locations
}
df = pd.DataFrame(data)

# Save the DataFrame to an Excel file
df.to_excel("bama_cars_requests_lib.xlsx", index=False)
