import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import sys
import time

headers = {
    "User-Agent": "Mozilla/5.0"
}

def normalize_url(url):
    parsed = urlparse(url)
    return parsed._replace(fragment="").geturl().rstrip('/')

def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for tag in soup.find_all("a"):
        href = tag.get("href")
        if href:
            full_url = urljoin(base_url, href.split("#")[0])
            if base_url in full_url:
                links.append(normalize_url(full_url))
    return links

def deep_crawl(start_url):
    visited = set()
    stack = [normalize_url(start_url)]
    all_found_links = []

    while stack:
        url = stack.pop()
        if url in visited:
            continue

        visited.add(url)
        print(f"[+] Crawling: {url}")
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if "text/html" not in resp.headers.get("Content-Type", ""):
                continue

            links = extract_links(resp.text, start_url)
            all_found_links.extend(links)  # Include duplicates

            for link in links:
                if link not in visited:
                    stack.append(link)

        except Exception as e:
            continue

        time.sleep(0.5)  # Politeness delay

    return all_found_links

def read_input_file(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python deep_crawler_all_links.py <input_file.txt>")
        sys.exit(1)

    input_file = sys.argv[1]
    root_urls = read_input_file(input_file)

    final_links = []

    for root in root_urls:
        print(f"\n[*] Starting deep crawl for: {root}")
        links = deep_crawl(root)
        final_links.extend(links)

    print(f"\n[+] Total links found (with duplicates): {len(final_links)}\n")
    for link in final_links:
        print(link)
