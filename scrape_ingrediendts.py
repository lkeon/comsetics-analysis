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
        for row in rows:
            links.append(row[0])  # Get first element

    return links


def get_data_dict(url):
    '''Get JSON from HTML and return dictionary.'''

    # get page and render HTML
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    # Get data from the id with data field
    div = soup.find('div', id='appData')
    json = div['data']

    # Convert extracted JSON data to Python dictionary
    data = chompjs.parse_js_object(json)

    return data


def extract_from_dict(dict_in):
    '''Extract data from input dict and return a dict.'''

    # Init and fill output dictionary
    data_page = dict_in['page']
    data_out = {}

    name = data_page['name']

    # If data present extract, otherwise return None
    if 'rating' in data_page.keys():
        data_out['rating'] = data_page['rating']
    else:
        data_out['rating'] = None

    if 'ratingValue' in data_page.keys():
        data_out['rating-value'] = data_page['ratingValue']
    else:
        data_out['rating-value'] = None

    if 'description' in data_page.keys():
        data_out['description'] = ''
        for paragraph in data_page['description']:
            try:
                data_out['description'] = (data_out['description'] + ' ' +
                                           paragraph['text'][0])
            except Exception:
                pass
    else:
        data_out['description'] = None

    if 'relatedCategories' in data_page.keys():
        data_out['categories'] = []
        for category in data_page['relatedCategories']:
            data_out['categories'].append(category['name'])
    else:
        data_out['categories'] = None

    if 'related' in data_page.keys():
        data_out['related-categories'] = []
        for category in data_page['related']:
            data_out['related-categories'].append(category['name'])
    else:
        data_out['related-categories'] = None

    if 'benefits' in data_page.keys():
        data_out['benefits'] = []
        for benefit in data_page['benefits']:
            data_out['benefits'].append(benefit['name'])
    else:
        data_out['benefits'] = None

    if 'references' in data_page.keys():
        data_out['references'] = data_page['references']
    else:
        data_out['references'] = None

    if 'key-points' in data_page.keys():
        data_out['key-points'] = data_page['keyPoints']
    else:
        data_out['key-points'] = None

    return {'name': name, 'data': data_out}


def convert_save_json(dict_in, json_name):
    '''Convert dict to JSON and save to disk.'''

    # Convert to JSON formatted string
    json_string = json.dumps(dict_in)

    # Write JSON to file
    with open(json_name, 'w') as out_file:
        out_file.write(json_string)


def main():
    '''Loop through pages and scrape ingredients data.'''

    # Get list of links containing ingredients
    csv = 'in.csv'
    links = read_csv_links(csv)
    # links = links[0:100]

    # Dictionary containing exracted data from all links
    ingredients = {}

    print('Scraping ...')

    # Get HTML page, extract JSON and convert to dict
    for link in tqdm(links):
        data_raw = get_data_dict(link)
        data_extract = extract_from_dict(data_raw)
        data_extract['link'] = link
        ingredient_name = data_extract['name']
        ingredients[ingredient_name] = data_extract['data']

    print('Scraping finished.')

    # Save JSON file
    file_save = 'out.json'
    convert_save_json(ingredients, file_save)
    print('Results saved as: ' + file_save)


if __name__ == '__main__':
    main()
