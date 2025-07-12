import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import sys
import time
import random
import os
import pyfiglet

# Matrix-style Gold Banner for ELSFA7-110
def gold_banner(name):
    yellow = "\033[93m"
    reset = "\033[0m"
    os.system('cls' if os.name == 'nt' else 'clear')

    # Fake "gold matrix" effect
    for _ in range(4):
        line = ''.join(random.choice(['$', '*', ' ', '.', ':']) for _ in range(70))
        print(yellow + line + reset)
        time.sleep(0.05)

    banner = pyfiglet.figlet_format(name)
    print(yellow + banner + reset)

    for _ in range(4):
        line = ''.join(random.choice(['$', '*', ' ', '.', ':']) for _ in range(70))
        print(yellow + line + reset)
        time.sleep(0.05)
    print()

gold_banner("ELSFA7-110")

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
}

def normalize_url(url):
    parsed = urlparse(url)
    return parsed._replace(fragment="").geturl().rstrip('/')

def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for tag in soup.find_all("a", href=True):
        href = tag.get("href")
        full_url = urljoin(base_url, href.split("#")[0])
        if base_url in full_url:
            links.add(normalize_url(full_url))
    return links

def deep_crawl(start_url):
    base_url = normalize_url(start_url)
    visited = set()
    to_visit = [base_url]
    found_links = set()

    while to_visit:
        url = to_visit.pop()
        if url in visited:
            continue

        visited.add(url)
        print(f"{url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if "text/html" not in response.headers.get("Content-Type", ""):
                continue

            links = extract_links(response.text, base_url)
            new_links = links - visited
            to_visit.extend(new_links)
            found_links.update(links)

        except requests.RequestException as e:
            print(f"[!] Failed: {url} ({e})")
            continue

        time.sleep(0.3)  # Slight delay for politeness

    return sorted(found_links)

def read_input_file(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 deep_gold_crawler.py <input_file.txt>")
        sys.exit(1)

    input_file = sys.argv[1]
    root_urls = read_input_file(input_file)

    all_links = set()

    for root_url in root_urls:
        print(f"\n[*] Starting full crawl on: {root_url}")
        links = deep_crawl(root_url)
        all_links.update(links)

    print(f"\n[✓] Total unique links found: {len(all_links)}\n")
    for link in all_links:
        print(link)
