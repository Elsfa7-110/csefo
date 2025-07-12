import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import sys
import time
import random
import os

# Matrix-style display of creator name
def matrix_effect(text):
    green = "\033[92m"
    reset = "\033[0m"
    for _ in range(3):  # Run multiple lines for matrix vibe
        line = ''.join(random.choice(['0', '1', ' ']) for _ in range(60))
        print(green + line + reset)
        time.sleep(0.05)
    print(green + f"### Coded by: {text} ###" + reset)
    for _ in range(3):
        line = ''.join(random.choice(['0', '1', ' ']) for _ in range(60))
        print(green + line + reset)
        time.sleep(0.05)
    print()

matrix_effect("ELSFA7-110")

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
    all_found_links = set()  # Use set to auto-remove duplicates

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
            for link in links:
                if link not in visited:
                    stack.append(link)
                all_found_links.add(link)

        except Exception as e:
            continue

        time.sleep(0.5)

    return list(all_found_links)

def read_input_file(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 csefo.py <input_file.txt>")
        sys.exit(1)

    input_file = sys.argv[1]
    root_urls = read_input_file(input_file)

    final_links = set()

    for root in root_urls:
        print(f"\n[*] Starting deep crawl for: {root}")
        links = deep_crawl(root)
        final_links.update(links)

    print(f"\n[+] Total unique links found: {len(final_links)}\n")
    for link in sorted(final_links):
        print(link)
