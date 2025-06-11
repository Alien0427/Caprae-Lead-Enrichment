import os
import requests

PROXYCURL_API_KEY = os.getenv("PROXYCURL_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
GOOGLE_CSE_API_KEY = os.getenv("GOOGLE_CSE_API_KEY")
GOOGLE_CSE_CX_ID = os.getenv("GOOGLE_CSE_CX_ID")
BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY")


def enrich_linkedin_company(linkedin_url):
    """
    Enrich company data using Proxycurl LinkedIn API.
    Returns a dictionary with enriched data or None if failed.
    """
    if not PROXYCURL_API_KEY:
        print("Proxycurl API key not set.")
        return None
    endpoint = "https://nubela.co/proxycurl/api/linkedin/company"
    params = {"url": linkedin_url}
    headers = {"Authorization": f"Bearer {PROXYCURL_API_KEY}"}
    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Proxycurl enrichment failed for {linkedin_url}: {e}")
        return None

def enrich_firecrawl_website(website_url):
    """
    Enrich company data using Firecrawl API (website scraping).
    Returns a dictionary with enriched data or None if failed.
    """
    if not FIRECRAWL_API_KEY:
        print("Firecrawl API key not set.")
        return None
    endpoint = "https://api.firecrawl.dev/v1/scrape"
    headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}"}
    json_data = {"url": website_url}
    try:
        response = requests.post(endpoint, headers=headers, json=json_data, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Firecrawl enrichment failed for {website_url}: {e}")
        return None

def enrich_hubspot_company(domain):
    """
    Enrich company data using HubSpot API (by domain).
    Returns a dictionary with enriched data or None if failed.
    """
    if not HUBSPOT_API_KEY:
        print("HubSpot API key not set.")
        return None
    endpoint = f"https://api.hubapi.com/companies/v2/companies/domain/{domain}"
    headers = {"Authorization": f"Bearer {HUBSPOT_API_KEY}"}
    try:
        response = requests.get(endpoint, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"HubSpot enrichment failed for {domain}: {e}")
        return None

def enrich_google_cse(company_name):
    """
    Enrich company data using Google Custom Search Engine (CSE).
    Returns a dictionary with search results or None if failed.
    """
    if not GOOGLE_CSE_API_KEY or not GOOGLE_CSE_CX_ID:
        print("Google CSE API key or CX ID not set.")
        return None
    endpoint = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_CSE_API_KEY,
        "cx": GOOGLE_CSE_CX_ID,
        "q": company_name
    }
    try:
        response = requests.get(endpoint, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Google CSE enrichment failed for {company_name}: {e}")
        return None

def enrich_brightdata(url_or_query):
    """
    Enrich company data using Bright Data API (web scraping or search).
    Returns a dictionary with enriched data or None if failed.
    """
    if not BRIGHTDATA_API_KEY:
        print("Bright Data API key not set.")
        return None
    endpoint = "https://api.brightdata.com/dca/trigger"
    headers = {"Authorization": f"Bearer {BRIGHTDATA_API_KEY}"}
    json_data = {
        "collector_id": "013d3e727f8a06419f9586b1182249481a66d0661192ac82692c220a97ea7c0f",  # Replace with actual collector ID
        "start_url": url_or_query
    }
    try:
        response = requests.post(endpoint, headers=headers, json=json_data, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Bright Data enrichment failed for {url_or_query}: {e}")
        return None 