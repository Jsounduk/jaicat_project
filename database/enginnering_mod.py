import requests
from bs4 import BeautifulSoup

# Define a function to search for engineering information on Wikipedia
def search_engineering_info(topic):
    url = "https://en.wikipedia.org/wiki/" + topic.replace(" ", "_")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    info_box = soup.find("table", class_="infobox vcard")
    if info_box:
        specs = {}
        for row in info_box.find_all("tr"):
            key = row.find("th")
            value = row.find("td")
            if key and value:
                specs[key.text.strip()] = value.text.strip()
        return specs
    else:
        return "Engineering topic not found"

# Example usage:
topic = "Mechanical Engineering"
result = search_engineering_info(topic)
print(result)