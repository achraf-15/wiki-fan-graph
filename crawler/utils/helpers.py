# crawler/utils/helpers.py

import requests
from urllib.parse import urlparse
import re
import time

   

def getdata(url):  
    #stop a Python script after 1 second
    startTime = time.time()
    timeToRun = 3
    endTime = startTime + timeToRun
    try:
        r = requests.get(url, timeout=timeToRun) 
        if (time.time() >= endTime):
            r = requests.get(url, timeout=timeToRun) 
    except:
        return None 
    return r.text if r.status_code == 200 else None

def extract_urls(soup, base_url):
    """Extract URLs from the soup object."""
    return [base_url + a['href'] for a in soup.find_all('a', class_='category-page__member-link')]

def clean_text(content):
    """ Remove references that usually appear as [ 1 ], [ 2 ], etc."""
    content = re.sub(r'\[ \d+\ ]', '', content)
    return content

def clean_filename(text: str) -> str:
    """Replaces '/', '-', and '.' with '_' in the given text."""
    return re.sub(r'[\/\-.]', '_', text)

def get_trailing_parts(url, base_url):
    base_path = urlparse(base_url).path.rstrip("/")  # Normalize base URL
    trailing_parts = urlparse(url).path.replace(base_path, "", 1).lstrip("/") 
    return trailing_parts


def process_hrefs(hrefs):
    """Process a list of <a> tags to extract URLs of the format 'wiki/name_of_page' and strip away the 'wiki/' part."""
    links = [(link['href'], link.text) for link in hrefs]
    processed_links = []

    for link, text in links:
        if link.startswith('/wiki/'):
            # Remove the '/wiki/' part and any section part after '#'
            processed_link = re.sub(r'^/wiki/|#.*$', '', link)
            processed_links.append((processed_link, text))

    return processed_links

def process_parg(parg):
    text = clean_text(parg.get_text(separator=' ', strip=True))
    links = process_hrefs(parg.find_all('a', href=True))
    return text, links