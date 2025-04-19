# crawler/url_collectors.py

from bs4 import BeautifulSoup
from crawler.utils.helpers import getdata, extract_urls
from config import BASE_URL

def process_characters_urls(url= 'https://onepiece.fandom.com/wiki/List_of_Canon_Characters'):
    response = getdata(url)
    if response:
        soup = BeautifulSoup(response, 'html.parser')
        table = soup.find('table')

        characters_urls = []
        if table:
            rows = table.find_all('tr')
            for row in rows:
                columns = row.find_all('td')
                if len(columns) >= 5:
                    first_column = columns[1]
                    link = first_column.find('a', href=True)
                    if link:
                        characters_urls.append(BASE_URL + link['href'])
        return characters_urls
    else:
        print(f"[WARN] Failed to load {url}.")
        return list()

def process_urls_recursively(url, base_url, depth, current_depth=0):
    if current_depth > depth:
        return []

    response = getdata(url)
    if response:
        soup = BeautifulSoup(response, 'html.parser')
        urls = extract_urls(soup, base_url)
        colons_urls = [u for u in urls if u.count(':') > current_depth]

        for colons_url in colons_urls:
            urls.extend(process_urls_recursively(colons_url, base_url, depth, current_depth + 1))

        return urls
    else:
        print(f"[WARN] Failed to load {url}.")
        return list()
