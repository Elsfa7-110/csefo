import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import sys
import time
import random
import os
import pyfiglet
import threading

# Banner displaying ELSFA7-110 in "gold" with matrix effect
def gold_banner(name):
    yellow = "\033[93m"
    reset = "\033[0m"
    os.system('cls' if os.name == 'nt' else 'clear')

    # Matrix-like effect
    for _ in range(4):
        line = ''.join(random.choice(['$', '*', ' ', '.', ':']) for _ in range(70))
        print(yellow + line + reset)
        time.sleep(0.05)

    # PyFiglet-style ASCII art
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

# Normalize URLs (remove fragment and ensure trailing slash)
def normalize_url(url):
    parsed = urlparse(url)
    return parsed._replace(fragment="").geturl().rstrip('/')

# Extract links from HTML content
def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for tag in soup.find_all("a", href=True):
        href = tag.get("href")
        full_url = urljoin(base_url, href.split("#")[0])
        if base_url in full_url:
            links.add(normalize_url(full_url))
    return links

# Simple vulnerability scan: checking for XSS, open redirects, and SQL injection
def scan_vulnerabilities(url, html):
    vulnerabilities = []
    
    # Check for potential XSS
    if "<script>" in html or "javascript:" in html:
        vulnerabilities.append("Potential XSS vulnerability detected.")
    
    # Check for open redirects
    if "redirect" in url or "url=" in url:
        vulnerabilities.append("Potential open redirect detected.")
    
    # Check for SQL Injection risk
    if "' OR 1=1 --" in url or "'; DROP TABLE" in url:
        vulnerabilities.append("Potential SQL Injection vulnerability detected.")
    
    return vulnerabilities

# Crawl a website recursively with threading and depth limit
def deep_crawl(start_url, depth_limit, visited, to_visit, found_links):
    base_url = normalize_url(start_url)
    visited.add(base_url)
    
    while to_visit:
        url = to_visit.pop()
        if url in visited or len(visited) > depth_limit:
            continue

        visited.add(url)
        print(f"{url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if "text/html" not in response.headers.get("Content-Type", ""):
                continue

            # Scan for vulnerabilities
            vulnerabilities = scan_vulnerabilities(url, response.text)
            if vulnerabilities:
                print(f"[!] Vulnerabilities found at {url}: {', '.join(vulnerabilities)}")
            
            links = extract_links(response.text, base_url)
            new_links = links - visited
            to_visit.extend(new_links)
            found_links.update(links)

        except requests.RequestException as e:
            print(f"[!] Failed: {url} ({e})")
            continue

        time.sleep(0.3)  # Politeness delay

# Read the input file (URLs to start the crawl)
def read_input_file(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

# Threading for concurrent crawling
def threaded_crawl(start_url, depth_limit, visited, to_visit, found_links):
    thread = threading.Thread(target=deep_crawl, args=(start_url, depth_limit, visited, to_visit, found_links))
    thread.start()
    thread.join()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 deep_gold_crawler_with_vuln_scan.py <input_file.txt> <depth_limit>")
        sys.exit(1)

    input_file = sys.argv[1]
    depth_limit = int(sys.argv[2])  # Set depth limit for crawl
    root_urls = read_input_file(input_file)

    visited = set()
    to_visit = []
    found_links = set()

    for root_url in root_urls:
        print(f"\n[*] Starting deep crawl for: {root_url} with depth limit {depth_limit}")
        to_visit.append(root_url)
        threaded_crawl(root_url, depth_limit, visited, to_visit, found_links)

    print(f"\n[✓] Total unique links found: {len(found_links)}\n")

    # Write to output file
    with open("found_links.txt", "w") as f:
        for link in found_links:
            f.write(link + "\n")

    print(f"[✓] Links saved to 'found_links.txt'.")
