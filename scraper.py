import requests
from bs4 import BeautifulSoup

def scrape_company_website(url):
    """
    Scrape basic company info from the given website URL.
    Returns a dictionary with scraped data or None if failed.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Example: Try to get meta description and title
        title = soup.title.string if soup.title else ''
        description = ''
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag and 'content' in desc_tag.attrs:
            description = desc_tag['content']
        return {
            'website_title': title,
            'website_description': description
        }
    except Exception as e:
        print(f"Scraping failed for {url}: {e}")
        return None 