import asyncio
import logging
from os import environ
from typing import Sequence

import httpx
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

MAX_CONCURRENT_REQUESTS = 5


async def query(
        semaphore: asyncio.Semaphore,
        search: str,
        fields: Sequence[str],
        boost_fields: Sequence[float]
) -> list[str]:

    async with semaphore:
        async with httpx.AsyncClient(auth=(environ['USER_SOLR'], environ['PASS_SOLR'])) as client:
            weighed_fields = [f'{fld}^{bst:.4f}' for fld, bst in zip(fields, boost_fields)]
            params = {
                'q': search,
                'rows': 100,
                'defType': 'edismax',
                'qf': ' '.join(weighed_fields)
            }
            response = await client.get(environ['URL_SOLR'] + '/select', params=params)
            response.raise_for_status()
            data = response.json()
            urls = []

            for hit in data['response']['docs']:
                if 'ss_url' in hit:
                    url = environ['URL_WEB'] + hit['ss_url']
                    if url not in urls:
                        urls.append(url)

        return urls


async def query_all(searches: list[str], fields: Sequence[str], boost_fields: Sequence[float]) -> list[list[str]]:
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    tasks = [query(semaphore, search, fields, boost_fields) for search in searches]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle exceptions
    for idx, result in enumerate(results):
        if isinstance(result, Exception):
            logging.error(f'Search query at index {idx} generated an exception: {result}')
            results[idx] = []  # Append empty list on failure

    return results


if __name__ == '__main__':
    target_fields = [
        'tm_X3b_en_body_value',
        'tm_X3b_en_field_ref_desc',
        'tm_X3b_en_field_ref_titre',
        'tm_X3b_en_mots_cles',
        'tm_X3b_en_title',
        'tm_X3b_en_corps_value',
        'tm_X3b_en_paragraphs_text',
        'tm_X3b_en_name',
        'tm_X3b_en_mission_value',
        'tm_X3b_en_text_content',
        # tm_X3b_en_full_meta_tag
    ]

    asyncio.run(
        query_all(pd.read_csv('dataset/queries.csv')['query'].str.replace('"', '').str.strip().unique(), target_fields,
                  [1] * len(target_fields)))
