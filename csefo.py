import requests
import re
import sys

def get_subdomains(domain):
    print(f"[+] Fetching subdomains for: {domain}")
    url = f"https://crt.sh/?q=%25.{domain}&output=json"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"[-] Failed to fetch data from crt.sh (status: {response.status_code})")
            return []

        entries = response.json()
        subdomains = set()
        for entry in entries:
            name_value = entry.get('name_value', '')
            for sub in name_value.split('\n'):
                if domain in sub:
                    subdomains.add(sub.strip())

        return sorted(subdomains)

    except Exception as e:
        print(f"[-] Error: {e}")
        return []

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_subdomains_crtsh.py <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    subdomains = get_subdomains(domain)

    print(f"\n[+] Found {len(subdomains)} unique subdomains:\n")
    for sub in subdomains:
        print(sub)
