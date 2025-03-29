# Web scraping logic

# import libraries
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import requests
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def get_internal_links(url, domian):
    """Extracts all internal links from a given webpage."""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if len(response.history) > 5:
            print(f"skipping {url} (Too many redirects)")
            return set()
        soup = BeautifulSoup(response.text, 'html.parser')

        links = set()
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(url, href)

            if urlparse(full_url).netloc == domian:
                links.add(full_url)
        return links 
    except Exception as e:
        print(f"Error fetching links from {url}: {e}")
        return set()
                

def uni_scrap(base_url):
    """crawls a university website to find graduate programs and funding information."""

    domain = urlparse(base_url).netloc
    visited = set()
    to_visit = {base_url}

    programs = ["data science", "machine learning", "computer science", "mathematics"]
    funding_keys = ["scholarships", "tuition waiver", "assistanship", "funding", "fellowship"]

    available_programs = set()
    available_funding = set()
    
    while to_visit:
        url = to_visit.pop()
        if url in visited:
            continue

        try:
            response = requests.get(url,headers=headers, timeout=10)
            if response.status_code != 200:
                continue

            visited.add(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text().lower()

            for program in programs:
                if re.search(rf"\b{program}\b", text):
                    available_programs.add(program)

            for funding in funding_keys:
                if re.search(rf"\b{funding}\b", text):
                    available_funding.add(funding)

            new_links = get_internal_links(url, domain)
            to_visit.update(new_links - visited)
        
        except Exception as e:
            print(f"Error scraping {url}: {e}")


    return {
        "School Url": url,
        "Programs Offered": ", ".join(available_programs) if available_programs else "Not Found",
        "Funding Available": ", ".join(available_funding) if available_funding else "Not Found"
    }

if __name__ == "__main__":
    print(uni_scrap("https://www.alasu.edu/"))