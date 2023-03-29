# Imported html products are sorted by sales.

from bs4 import BeautifulSoup
import csv
import re

html_in = 'saved.html'
csv_out = 'out.csv'

with open(html_in, 'r', encoding='utf8') as f:
    contents = f.read()

soup = BeautifulSoup(contents, 'html.parser')
links = soup.find_all('a', class_='css-klx76')

# Extract span elements selected by filtered regular expression
companies = soup.find_all('span',
    attrs={'class': re.compile('css-bpsjlq.*')})

names = soup.find_all('span',
    attrs={'class': re.compile('ProductTile-name css-.*')})

assert(len(links) == len(companies) and len(companies) == len(names))

filew = open(csv_out, 'w', encoding='utf8', newline='')
writer = csv.writer(filew)
writer.writerow(['Company', 'Name', 'Bestselling', 'Link'])

for num, entry in enumerate(zip(companies, names, links)):
    company = entry[0].text
    name = entry[1].text
    link = entry[2]['href']

    writer.writerow([company, name, num, link])

    print(company)
    print(name)
    print(link)
    print('--------------------')

filew.close()
print("Num of all elements parsed: " + str(len(links)))
