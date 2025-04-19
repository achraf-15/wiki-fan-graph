# crawler/crawler.py

from crawler.parsers.page_processor import PageProcessor
from crawler.url_collectors import process_characters_urls, process_urls_recursively
from crawler.utils.json_writer import  load_saved_urls, delete_saved_urls
from config import WIKI_URL, BASE_URL, DATA_DIR

from tqdm import tqdm 

def crawl(update_only=False, verbose=1):

    if update_only:
        try:
            saved_urls = load_saved_urls(DATA_DIR)
        except FileNotFoundError:
            print(f"[WARN] Failed to load saved urls from {DATA_DIR}.")
            if verbose:
                print("Create a new list...")
            saved_urls = set()
    else:
        saved_urls = set()
        delete_saved_urls(DATA_DIR)

    if verbose >= 2:
        print("-----"*10)

    processor = PageProcessor(wiki_base_url=WIKI_URL, data_dir=DATA_DIR, update_only=update_only, saved_pages=saved_urls)

    all_urls = []

    # Characters URLs
    if verbose:
        print("Fetching Characters pages...")
    characters_urls = process_characters_urls(url= 'https://onepiece.fandom.com/wiki/List_of_Canon_Characters')
    all_urls.extend([(chr_url, 'Character') for chr_url in characters_urls])

    if verbose >= 2:
        print("Number of Characters pages :", len(set(characters_urls)))
        print("-----"*10)
    
    # Subtances URLs
    if verbose:
        print("Fetching Substances pages...")
    start_url = 'https://onepiece.fandom.com/wiki/Category:Substances'
    depth = 3  # Set the desired recursion depth
    subtances_urls = process_urls_recursively(start_url, BASE_URL, depth)
    subtances_urls = [(u, 'Subtances') for u in subtances_urls if u.count(':') == 1 and u.count('/') == 4] # Only keep the pages urls
    all_urls.extend(subtances_urls)
    
    if verbose >= 2:
        print("Number of Substances pages :", len(set(subtances_urls)))
        print("-----"*10)

    # Geography URLs
    if verbose:
        print("Fetching Geography pages...")
    start_url = 'https://onepiece.fandom.com/wiki/Category:Geography'
    depth = 2  # Set the desired recursion depth
    geography_urls = process_urls_recursively(start_url, BASE_URL, depth)
    geography_urls = [(u, 'Geography') for u in geography_urls if u.count(':') == 1 and u.count('/') == 4] # Only keep the pages urls] 
    all_urls.extend(geography_urls)

    if verbose >= 2:
        print("Number of Geography pages :", len(set(geography_urls)))
        print("-----"*10)

    # Societ_Culture URLs
    if verbose:
        print("Fetching Society and Culture pages...")
    start_url = 'https://onepiece.fandom.com/wiki/Category:Society_and_Culture'
    depth = 2  # Set the desired recursion depth
    society_culture_urls = process_urls_recursively(start_url, BASE_URL, depth)
    society_culture_urls = [(u, 'Societ_Culture') for u in society_culture_urls if u.count(':') == 1 and u.count('/') == 4] # Only keep the pages urls
    all_urls.extend(society_culture_urls)

    if verbose >= 2:
        print("Number of Society and Culture pages :", len(set(society_culture_urls)))
        print("-----"*10)

    # History URLs
    if verbose:
        print("Fetching History pages...")
    start_url = 'https://onepiece.fandom.com/wiki/Category:History'
    depth = 3  # Set the desired recursion depth
    history_urls = process_urls_recursively(start_url, BASE_URL, depth)
    history_urls = [(u, 'History') for u in history_urls if u.count(':') == 1 and u.count('/') == 4] # Only keep the pages urls
    all_urls.extend(history_urls)
    
    if verbose >= 2:
        print("Number of History pages :", len(set(history_urls)))
        print("-----"*10)

    # Organizations URLs
    if verbose:
        print("Fetching Organizations pages...")
    start_url = 'https://onepiece.fandom.com/wiki/Category:Organizations'
    depth = 3  # Set the desired recursion depth
    organizations_urls = process_urls_recursively(start_url, BASE_URL, depth)
    organizations_urls = [(u, 'Organizations') for u in organizations_urls if u.count(':') == 1 and u.count('/') == 4] # Only keep the pages urls
    all_urls.extend(organizations_urls)

    if verbose >= 2:
        print("Number of Organizations pages :", len(set(organizations_urls)))
        print("-----"*10)

    URLs = list(set(all_urls))
    if verbose:
        print("URLs Collection finished.")
    if verbose >= 2:
        print("Total of ",len(URLs)," pages.")
        print("-----"*10)

    if verbose:
        print(DATA_DIR, "already has", len(saved_urls), "saved pages!")
    if verbose >= 2:
        if update_only:
            print("update_only enabled!")
        print("-----"*10)


    
    for url, category in tqdm(URLs, desc="Parsing "+BASE_URL, disable=(verbose<2)):
        """try: 
            processor.process(url)
        except KeyError: 
            continue""" 
        processor.process(url, category)

    if verbose :
        print("Parsing finished.")
    if verbose >= 2:
        print("-----"*10)

    