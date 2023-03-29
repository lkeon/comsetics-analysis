# Scrape Skincare Ingredients

from requests_html import HTMLSession
from bs4 import BeautifulSoup
import csv

# Get the page and render JavaScript
url = ''
session = HTMLSession()
r = session.get(url)
r.html.render(timeout=20)

# Convert to BeautifulSoup bject and find all divs with link
soup = BeautifulSoup(r.html.raw_html, 'html.parser')
results = soup.find_all('div', class_='IngredientList__ReadMore-sc-1nbipyf-12 hVILA-d small1 uppercase')
print(len(results))

# Loop through all divs and extract links
filesave = 'out.csv'
prefix = ''  # Main website URL

file = open(filesave, 'w')
writer = csv.writer(file)

for div in results:
    link = div.find('a')['href']
    writer.writerow([prefix + link])

file.close()
