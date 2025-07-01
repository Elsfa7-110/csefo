import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
import sys
import threading
import queue

visited = set()
lock = threading.Lock()
q = queue.Queue()

def fetch_sitemaps(base_url):
    sitemaps = set()

    # 1. Try default location
    default_sitemap = urljoin(base_url, "/sitemap.xml")
    try:
        r = requests.get(default_sitemap, timeout=5)
        if r.status_code == 200 and "<urlset" in r.text:
            print(f"[+] Found sitemap at: {default_sitemap}")
            sitemaps.add(default_sitemap)
    except:
        pass

    # 2. Look for sitemap in robots.txt
    robots_url = urljoin(base_url, "/robots.txt")
    try:
        r = requests.get(robots_url, timeout=5)
        if r.status_code == 200:
            matches = re.findall(r"Sitemap:\s*(\S+)", r.text)
            for match in matches:
                sitemaps.add(match.strip())
    except:
        pass

    return list(sitemaps)

def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for tag in soup.find_all(["a", "area"]):
        href = tag.get("href")
        if href:
            href = urljoin(base_url, href.split('#')[0])  # Remove anchors
            parsed = urlparse(href)
            if parsed.scheme.startswith("http"):
                links.add(href)
    return links

def crawl(url, base_domain):
    try:
        r = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if "text/html" not in r.headers.get("Content-Type", ""):
            return
        links = extract_links(r.text, url)

        for link in links:
            parsed = urlparse(link)
            if base_domain in parsed.netloc:
                with lock:
                    if link not in visited:
                        visited.add(link)
                        q.put(link)
    except Exception as e:
        pass

def worker(base_domain):
    while True:
        url = q.get()
        if url is None:
            break
        crawl(url, base_domain)
        q.task_done()

def start_crawling(start_url, max_threads=5):
    parsed_start = urlparse(start_url)
    base_domain = parsed_start.netloc

    visited.add(start_url)
    q.put(start_url)

    threads = []
    for _ in range(max_threads):
        t = threading.Thread(target=worker, args=(base_domain,))
        t.daemon = True
        t.start()
        threads.append(t)

    q.join()

    for _ in threads:
        q.put(None)
    for t in threads:
        t.join()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python crawler_with_links_and_sitemaps.py <https://example.com>")
        sys.exit(1)

    start_url = sys.argv[1]

    print("[*] Starting crawl...")
    start_crawling(start_url)

    print(f"\n[+] Total unique internal links found: {len(visited)}")
    for link in sorted(visited):
        print(link)

    print("\n[*] Checking for sitemap(s)...")
    sitemaps = fetch_sitemaps(start_url)
    if sitemaps:
        for sm in sitemaps:
            print(f"[+] Sitemap: {sm}")
    else:
        print("[-] No sitemap found.")
