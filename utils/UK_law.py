import requests
from bs4 import BeautifulSoup

# Define a function to search for UK Law information
def search_uk_law(query):
    url = "https://www.legislation.gov.uk/search"
    params = {"q": query}
    response = requests.get(url, params=params)
    soup = BeautifulSoup(response.content, "html.parser")
    results = []
    for result in soup.find_all("div", class_="result"):
        title = result.find("h2", class_="title").text.strip()
        link = result.find("a", href=True)["href"]
        results.append({"title": title, "link": link})
    return results

# Example usage:
query = "data protection"
results = search_uk_law(query)
for result in results:
    print(f"{result['title']} - {result['link']}")
