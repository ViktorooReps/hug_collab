import json
from os import environ

from dotenv import load_dotenv
from tqdm import tqdm

import pandas as pd
import requests
from bs4 import BeautifulSoup


load_dotenv()


def get_search_results(query: str) -> list[str]:
    # Performing a search
    session = requests.Session()
    session.auth = (environ['USER_WEB'], environ['PASS_WEB'])
    query = query.replace(' ', '+')
    response = session.get(
        f'{environ['URL_WEB']}/en/search?keys={query}',
        headers={'Content-Type': 'application/json'}
    )

    html_content = response.content

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all <a> tags within the search results
    search_results = soup.find_all('li', class_='search-result')

    # Extract the URLs from the href attributes of the <a> tags
    urls = [environ['URL'] + result.find('a')['href'] for result in search_results]

    return urls


if __name__ == '__main__':
    query2results = {}
    for query in tqdm(pd.read_csv('dataset/queries.csv')['query'].str.replace('"', '').str.strip().unique()):
        query2results[query] = get_search_results(query)

    with open('results/results_scraped_initial_version.json', 'w') as f:
        json.dump(query2results, f, indent=4)
