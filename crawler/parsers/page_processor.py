# crawler/parsers/page_processor.py

import re
from typing import List, Tuple
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from crawler.utils.helpers import (
    getdata,
    get_trailing_parts,
    process_parg,
)

from crawler.schemas import ChunkData, DocumentData
from crawler.utils.json_writer import save_data, save_graph, save_doc, save_url


class PageProcessor:
    def __init__(self, wiki_base_url: str, data_dir: str, update_only=False, saved_pages=set()):
        """
        :param wiki_base_url: Base URL for the wiki (used for title extraction).
        :param persist: Whether to persist extracted data to disk.
        """
        self.wiki_base_url = wiki_base_url
        self.data_dir = data_dir
        self.processed_pages = set()
        self.update_only = update_only
        self.saved_pages = saved_pages


    def process(self, url: str, category: str, include_subpages: bool = True) -> None:
        """
        Main entry point. Given a URL, optionally includes subpages and processes all of them.
        Returns parsed documents, chunk data, and the link graph.
        """
        pages_to_parse = [url]
        if include_subpages:
            pages_to_parse.extend(self._extract_subpages(url))

        for page_url in set(pages_to_parse):
            if not(page_url in self.processed_pages): 
                if self.update_only:
                    if page_url in self.saved_pages:
                        continue
                result = self._parse_page(page_url, category)
                if result:
                    doc, chunks, graph = result
                    self.processed_pages.add(page_url)

                    if self.data_dir:
                        title = get_trailing_parts(page_url, self.wiki_base_url)
                        save_doc(doc, title, outdir=self.data_dir)
                        save_data(chunks, title, outdir=self.data_dir)
                        save_graph(graph, title, outdir=self.data_dir)
                        save_url(url, outdir=self.data_dir)

    def _extract_subpages(self, url: str) -> List[str]:
        """
        Extracts subpage URLs by scanning for internal links under the same base URL.
        """
        if self.update_only:
            if url in self.saved_pages:
                return list()
        
        response = getdata(url)
        if response:
            soup = BeautifulSoup(response, "html.parser")
            subpages = []
            for link in soup.find_all("a", href=True):
                full_url = urljoin(url, link["href"])
                if full_url.startswith(url + '/') and full_url.count('#') == 0:
                    subpages.append(full_url)
            return subpages
        else :
            print(f"[WARN] Failed to load {url}.")
            return list()

    def _parse_page(self, url: str, category: str) -> Tuple[DocumentData, List[ChunkData], dict]:
        """
        Parses a single wiki page, returning its metadata, extracted chunks, and link graph.
        """
        response = getdata(url)
        if response:
            soup = BeautifulSoup(response, 'html.parser')
            title = get_trailing_parts(url, self.wiki_base_url)
            sections = [section.parent for section in soup.find_all('span', class_="mw-headline")]

            chunks = []
            graph = {}
            chunk_id = 0

            for section in sections:
                section_text, section_links = self._parse_section(section)
                section_text = re.sub(r'\s+', ' ', section_text).strip()
                token_count = len(section_text.split())

                if token_count:
                    chunk_id += 1
                    chunk = ChunkData(
                        url=url,
                        chunk_id=f"{title}_{chunk_id}",
                        title=title,
                        category = category,
                        text=section_text,
                        section=section.span['id'],
                        links=section_links,
                        token_count=token_count
                    )
                    chunks.append(chunk)
                    graph.setdefault(title, []).append((chunk.chunk_id, 'chunk'))
                    if section_links:
                        graph.setdefault(chunk.chunk_id, []).extend(section_links)

            page_start = soup.find('p') 
            doc_overview, doc_links  = self._parse_overview(page_start)
            doc_overview = re.sub(r'\s+', ' ', doc_overview).strip()
            for L in graph.values():
                doc_links.extend(L)
            
            document = DocumentData(
                url=url,
                title=title,
                category = category,
                text = doc_overview,
                links=doc_links
            )

            return document, chunks, graph
        else:
            print(f"[WARN] Failed to load {url}.")
            return None

    def _parse_section(self, section_tag) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Parses a single section of a wiki page, extracting clean text and links.
        """
        section_text = ""
        section_links = []
        next_element = section_tag.find_next_sibling()

        while next_element and not(next_element.name in ['h2','h3','h4']): 
            if next_element.name == 'p':
                text, links = process_parg(next_element)
                section_text += text + "\n"
                section_links.extend(links)

            elif next_element.name == 'ul':
                for li in next_element.find_all('li'):
                    text, links = process_parg(li)
                    section_text += text + "\n"
                    section_links.extend(links)

            next_element = next_element.find_next_sibling()

        return section_text, section_links


    def _parse_overview(self, section_tag) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Parses a single section of a wiki page, extracting clean text and links.
        """
        section_text = ""
        section_links = []

        while section_tag and section_tag.name == 'p': 
            text, links = process_parg(section_tag)
            section_text += text + "\n"
            section_links.extend(links)

            section_tag = section_tag.find_next_sibling()

        return section_text, section_links
