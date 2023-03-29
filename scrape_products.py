''' This package scrapes ingrediends from a
website. It contains several function to import links
of all ingredients and to scrape their propertiers to
Python dictionary and JSON file.
'''
from bs4 import BeautifulSoup
from tqdm import tqdm
import requests
import chompjs
import json
import csv


def read_csv_links(filepath):
    ''' Read CSV file with links and return a list.'''

    links = []

    with open(filepath) as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        next(rows, 'None')  # Skip header
        for row in rows:
            links.append(row[3])  # Get first element

    return links


def get_data_dict(url):
    '''Get JSON from HTML and return dictionary.'''

    # get page and render HTML
    hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0'}
    page = requests.get(url, timeout=8, headers=hdr)
    soup = BeautifulSoup(page.text, 'html.parser')

    # Get data from the id with data field
    script = soup.find('script', id='linkStore')
    json = script.text

    # Convert extracted JSON data to Python dictionary
    data = chompjs.parse_js_object(json)

    return data


def extract_from_dict(dict_in):
    '''Extract data from input dict and return a dict.'''

    # Init and fill output dictionary
    data = dict_in['page']['product']
    data_out = {}

    try:
        data_out['highlights'] = data['currentSku']['highlights']
    except Exception:
        data_out['highlights'] = None

    try:
        data_out['ingredients'] = data['currentSku']['ingredientDesc']
    except Exception:
        data_out['ingredients'] = None

    try:
        data_out['price'] = data['currentSku']['listPrice']
    except Exception:
        data_out['price'] = None

    try:
        data_out['replenish'] = {'num': data['currentSku']['replenishmentFreqNum'],
                                 'type': data['currentSku']['replenishmentFreqType']}
    except Exception:
        data_out['replenish'] = None
    
    try:
        data_out['size'] = data['currentSku']['size']
    except Exception:
        data_out['size'] = None

    try:
        category = data['parentCategory']
        data_out['category'] = [category['displayName']]

        while 'parentCategory' in category.keys():
            category = category['parentCategory']
            data_out['category'].append(category['displayName'])
    except Exception:
        data_out['category'] = None

    data_out['brand'] = data['productDetails']['brand']['displayName']
    
    try:
        data_out['brand-text'] = data['productDetails']['brand']['description']
    except Exception:
        data_out['brand-text'] = None

    try:
        data_out['brand-text-long'] = data['productDetails']['brand']['longDescription']
    except Exception:
        data_out['brand-text-long'] = None

    name = data['productDetails']['displayName']
    data_out['product'] = name
    
    try:
        data_out['product-text'] = data['productDetails']['longDescription']
    except Exception:
        data_out['product-text'] = None

    try:
        data_out['product-text-short'] = data['productDetails']['shortDescription']
    except Exception:
        data_out['product-text-short'] = None

    try:
        data_out['loves-count'] = data['productDetails']['lovesCount']
    except Exception:
        data_out['loves-count'] = None

    try:
        data_out['rating'] = data['productDetails']['rating']
    except Exception:
        data_out['rating'] = None

    try:
        data_out['reviews'] = data['productDetails']['reviews']
    except Exception:
        data_out['reviews'] = None

    try:
        data_out['usage'] = data['productDetails']['suggestedUsage']
    except Exception:
        data_out['usage'] = None

    return {'name': name, 'data': data_out}


def convert_save_json(dict_in, json_name):
    '''Convert dict to JSON and save to disk.'''

    # Convert to JSON formatted string
    json_string = json.dumps(dict_in)

    # Write JSON to file
    with open(json_name, 'w') as out_file:
        out_file.write(json_string)


def main():
    '''Loop through pages and scrape products data.'''

    csv_in = 'in.csv'
    file_save = 'out.json'

    # Get list of links containing products
    links = read_csv_links(csv_in)
    # links = links[355:365]
    num_txt = '/' + str(len(links))

    # Dictionary containing exracted data from all links
    products = {}

    print('Scraping ...')

    # Get HTML page, extract JSON and convert to dict
    for num, link in enumerate(tqdm(links)):
        data_raw = get_data_dict(link)
        data_extract = extract_from_dict(data_raw)
        data_extract['data']['link'] = link
        data_extract['data']['bestselling'] = str(num+1) + num_txt
        product_name = data_extract['name']
        products[product_name] = data_extract['data']

    print('Scraping finished.')

    # Save JSON file
    convert_save_json(products, file_save)
    print('Results saved as: ' + file_save)


if __name__ == '__main__':
    main()
