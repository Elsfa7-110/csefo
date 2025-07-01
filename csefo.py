import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import sys
import time

visited = set()
headers = {
    "User-Agent": "Mozilla/5.0"
}

def normalize_url(url):
    """Remove fragments and trailing slashes for consistency."""
    parsed = urlparse(url)
    return parsed._replace(fragment="").geturl().rstrip('/')

def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for tag in soup.find_all("a"):
        href = tag.get("href")
        if href:
            joined = urljoin(base_url, href.split("#")[0])
            if base_url in joined:
                links.add(normalize_url(joined))
    return links

def deep_crawl(start_url):
    stack = [normalize_url(start_url)]
    local_visited = set()

    while stack:
        url = stack.pop()
        if url in visited:
            continue

        print(f"[+] Crawling: {url}")
        visited.add(url)
        local_visited.add(url)

        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if "text/html" not in resp.headers.get("Content-Type", ""):
                continue

            links = extract_links(resp.text, start_url)
            for link in links:
                if link not in visited:
                    stack.append(link)

        except Exception as e:
            continue

        time.sleep(0.5)  # Be polite

    return local_visited

def read_input_file(file_path):
    with open(file_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python deep_crawler.py <input_file.txt>")
        sys.exit(1)

    input_file = sys.argv[1]
    urls = read_input_file(input_file)
    all_links = set()

    for root_url in urls:
        print(f"\n[*] Starting deep crawl for: {root_url}")
        root_links = deep_crawl(root_url)
        all_links.update(root_links)

    print(f"\n[+] Total unique links found: {len(all_links)}\n")
    for link in sorted(all_links):
        print(link)
