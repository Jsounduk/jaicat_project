import requests
from bs4 import BeautifulSoup

# Define a function to search for motorbike information on Wikipedia
def search_motorbike_info(motorbike):
    url = "https://en.wikipedia.org/wiki/" + motorbike.replace(" ", "_")
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
        return "Motorbike not found"

# Example usage:
motorbike = "Honda CB500F"
result = search_motorbike_info(motorbike)
print(result)