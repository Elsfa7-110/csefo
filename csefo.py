import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import sys
import time

visited_links = set()
wayback_links = set()

def get_links_from_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for tag in soup.find_all('a'):
        href = tag.get('href')
        if href:
            full_url = urljoin(base_url, href.split('#')[0])
            if base_url in full_url:
                links.add(full_url)
    return links

def crawl(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200 and 'text/html' in r.headers.get('Content-Type', ''):
            links = get_links_from_html(r.text, url)
            return links
    except Exception as e:
        pass
    return set()

def get_wayback_urls(domain):
    print(f"[*] Fetching Wayback URLs for {domain}")
    try:
        url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=text&fl=original&collapse=urlkey"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            lines = r.text.strip().split("\n")
            return set(lines)
    except Exception as e:
        pass
    return set()

def process_input_file(file_path):
    with open(file_path, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    return urls

def extract_root(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python crawler_with_wayback.py <input_links_file.txt>")
        sys.exit(1)

    input_file = sys.argv[1]
    input_urls = process_input_file(input_file)

    all_internal_links = set()
    all_wayback_links = set()
    seen_domains = set()

    for url in input_urls:
        print(f"\n[+] Crawling: {url}")
        base = extract_root(url)

        # Crawl live site
        internal_links = crawl(base)
        all_internal_links.update(internal_links)
        for link in internal_links:
            visited_links.add(link)

        # Wayback recon
        if base not in seen_domains:
            seen_domains.add(base)
            wb_links = get_wayback_urls(base)
            wayback_links.update(wb_links)

        time.sleep(1)  # Politeness

    print(f"\n[+] Total unique internal links found: {len(all_internal_links)}")
    for link in sorted(all_internal_links):
        print(link)

    print(f"\n[+] Total Wayback URLs found: {len(wayback_links)}")
    for link in sorted(wayback_links):
        print(link)
