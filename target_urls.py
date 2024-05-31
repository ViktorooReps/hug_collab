from os import environ

import requests
import solr
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Connecting to Solr server
s = solr.Solr(environ['URL_SOLR'], http_user=environ['USER_SOLR'], http_pass=environ['PASS_SOLR'])

if __name__ == '__main__':
    # Performing a search
    session = requests.Session()
    session.auth = (environ['USER_WEB'], environ['PASS_WEB'])

    response = s.select('ss_url:\\/en\\/csfe*', rows=100)

    urls = []
    for hit in response.results:
        url = environ['URL_WEB'] + hit['ss_url']
        urls.append(url)

    response = s.select('ss_url:\\/en\\/actualite\\/csfe*', rows=100)

    for hit in response.results:
        url = environ['URL_WEB'] + hit['ss_url']
        urls.append(url)

    pd.DataFrame(sorted(set(urls)), columns=['url']).to_csv('dataset/urls.csv', index=False)
