import os
from dotenv import load_dotenv
load_dotenv() 
import streamlit as st
import pandas as pd
from api_clients import (
    enrich_linkedin_company,
    enrich_firecrawl_website,
    enrich_hubspot_company,
    enrich_google_cse,
    enrich_brightdata
)
from qa_logic import score_lead
import gspread
from google.oauth2.service_account import Credentials
import re
import spacy
import requests
import json

st.set_page_config(page_title="Caprae Lead QA Tool", layout="wide")

# ---- UI / Styling -----------------------------------------------------------
# Inject custom CSS for glassmorphism background cards and subtle hover effects
st.markdown(
    """
    <style>
    /* overall deep-sea gradient background */
    body {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    }

    /* glass card look */
    .glass-card {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 18px;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        padding: 2rem 1.5rem;
        transition: all 0.2s ease-in-out;
    }
    .glass-card:hover {
        transform: translateY(-4px);
        border-color: rgba(255, 255, 255, 0.3);
    }

    /* nicer buttons on hover */
    button[kind="primary"], button[kind="secondary"] {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    button[kind="primary"]:hover, button[kind="secondary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.35);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Header -----------------------------------------------------------------
# Horse symbol and inspirational tagline
horse = "🐎"
st.markdown(
    f"<h1 style='font-size:3rem;font-weight:800;margin-bottom:0;color:#F5F5F5;'>{horse} Caprae Lead QA Tool</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h3 style='margin-top:4px;color:#cccccc;font-weight:400;'>Great Founders Working with Great Founders</h3>",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------

# Search form
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
with st.form("search_form"):
    industry = st.text_input("Industry", value="finance")
    location = st.text_input("Location", value="California")
    submitted = st.form_submit_button("Search Companies")

st.markdown("</div>", unsafe_allow_html=True)

# Helper for Google Sheets export
def export_to_gsheet(df, sheet_name="Caprae_Leads"): 
    try:
        creds = Credentials.from_service_account_file('service_account.json', scopes=["https://www.googleapis.com/auth/spreadsheets"])
        gc = gspread.authorize(creds)
        sh = gc.create(sheet_name)
        worksheet = sh.get_worksheet(0)
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        return sh.url
    except Exception as e:
        st.error(f"Google Sheets export failed: {e}")
        return None

# State abbreviation mapping
state_map = {
    'california': 'CA', 'new york': 'NY', 'texas': 'TX', 'illinois': 'IL', 'florida': 'FL',
    'massachusetts': 'MA', 'washington': 'WA', 'georgia': 'GA', 'pennsylvania': 'PA', 'ohio': 'OH',
    'michigan': 'MI'
}

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found. Please add it to your .env file or environment variables.")

def gemini_extract_info(snippet):
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=" + GEMINI_API_KEY
    headers = {"Content-Type": "application/json"}
    prompt = f"""
    Extract the employee count from this text: {snippet}
    """
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=20)
        response.raise_for_status()
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        try:
            info = json.loads(text)
            if 'candidates' not in result:
                print("Prompt blocked or empty response:", result)
                return {}
            return info
        except Exception:
            info = {}
            emp_match = re.search(r'employee_count[":\s]*([\d,]+)', text)
            if emp_match:
                info['employee_count'] = emp_match.group(1)
            rev_match = re.search(r'revenue[":\s]*([\d,]+)', text)
            if rev_match:
                info['revenue'] = rev_match.group(1)
            loc_match = re.search(r'location[":\s]*([a-zA-Z ,]+)', text)
            if loc_match:
                info['location'] = loc_match.group(1)
            ind_match = re.search(r'industry[":\s]*([a-zA-Z &]+)', text)
            if ind_match:
                info['industry'] = ind_match.group(1)
            year_match = re.search(r'year_founded[":\s]*(\d{4})', text)
            if year_match:
                info['year_founded'] = year_match.group(1)
            linkedin_match = re.search(r'linkedin_url[":\s]*(https?://[\w./-]+)', text)
            if linkedin_match:
                info['linkedin_url'] = linkedin_match.group(1)
            twitter_match = re.search(r'twitter_url[":\s]*(https?://[\w./-]+)', text)
            if twitter_match:
                info['twitter_url'] = twitter_match.group(1)
            facebook_match = re.search(r'facebook_url[":\s]*(https?://[\w./-]+)', text)
            if facebook_match:
                info['facebook_url'] = facebook_match.group(1)
            founders_match = re.search(r'founders[":\s]*([a-zA-Z ,&]+)', text)
            if founders_match:
                info['founders'] = founders_match.group(1)
            ceo_match = re.search(r'ceo[":\s]*([a-zA-Z .]+)', text)
            if ceo_match:
                info['ceo'] = ceo_match.group(1)
            funding_match = re.search(r'total_funding[":\s]*([\d,]+)', text)
            if funding_match:
                info['total_funding'] = funding_match.group(1)
            last_round_match = re.search(r'last_funding_round[":\s]*([a-zA-Z0-9 $,.]+)', text)
            if last_round_match:
                info['last_funding_round'] = last_round_match.group(1)
            investors_match = re.search(r'investors[":\s]*([a-zA-Z ,&]+)', text)
            if investors_match:
                info['investors'] = investors_match.group(1)
            return info
    except Exception as e:
        if 'response' in locals():
            print("Status:", response.status_code)
            print("Body:", response.text[:500])   # first 500 chars
        print(f"Gemini LLM extraction failed: {e}")
        return {}

def gemini_lead_scoring(company):
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=" + GEMINI_API_KEY
    headers = {"Content-Type": "application/json"}
    prompt = f"""
    Given the following company data, score the lead as 'Green' (strong fit), 'Yellow' (partial fit), or 'Red' (not a fit) for acquisition, and provide a short justification. Data: {json.dumps(company)}. Respond as JSON: {{'score': 'Green/Yellow/Red', 'justification': '...'}}
    """
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=20)
        response.raise_for_status()
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        try:
            info = json.loads(text)
            return info.get('score', None), info.get('justification', None)
        except Exception:
            score_match = re.search(r'score[":\s]*([A-Za-z]+)', text)
            just_match = re.search(r'justification[":\s]*([^\"]+)', text)
            score = score_match.group(1) if score_match else None
            justification = just_match.group(1) if just_match else None
            return score, justification
    except Exception as e:
        print(f"Gemini lead scoring failed: {e}")
        return None, None

def get_news_buzz(company_name: str, industry: str = None) -> dict:
    """Get recent news mentions and sentiment using Google News API."""
    try:
        # Use Google News RSS feed since the API is deprecated
        news_url = f"https://news.google.com/rss/search?q={company_name}+{industry if industry else ''}&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(news_url, timeout=10)
        response.raise_for_status()
        
        # Parse RSS feed
        from xml.etree import ElementTree
        root = ElementTree.fromstring(response.content)
        items = root.findall('.//item')
        
        news_data = {
            'recent_mentions': len(items),
            'latest_news': [],
            'sentiment_score': 0  # Simple sentiment based on title keywords
        }
        
        positive_words = {'growth', 'launch', 'expand', 'raise', 'funding', 'partnership', 'acquisition', 'success'}
        negative_words = {'layoff', 'decline', 'loss', 'down', 'struggle', 'challenge', 'risk'}
        
        for item in items[:5]:  # Analyze top 5 news items
            title = item.find('title').text.lower()
            pub_date = item.find('pubDate').text
            link = item.find('link').text
            
            news_data['latest_news'].append({
                'title': title,
                'date': pub_date,
                'link': link
            })
            
            # Simple sentiment scoring
            words = set(title.split())
            if words & positive_words:
                news_data['sentiment_score'] += 1
            if words & negative_words:
                news_data['sentiment_score'] -= 1
                
        return news_data
    except Exception as e:
        print(f"News API error: {e}")
        return {'recent_mentions': 0, 'latest_news': [], 'sentiment_score': 0}

def gemini_buy_intent(company: dict):
    """Enhanced buy intent classification using multiple signals, with fallback if Gemini fails."""
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    # Get news buzz data
    news_data = get_news_buzz(
        company.get('Company Name', ''),
        company.get('Industry', '')
    )
    
    # Prepare signals for the prompt
    signals = {
        'company_name': company.get('Company Name', ''),
        'industry': company.get('Industry', ''),
        'employee_count': company.get('Employee Count', ''),
        'revenue': company.get('Revenue', ''),
        'funding': company.get('Total Funding', ''),
        'last_funding': company.get('Last Funding Round', ''),
        'news_mentions': news_data['recent_mentions'],
        'news_sentiment': news_data['sentiment_score'],
        'latest_news': [n['title'] for n in news_data['latest_news'][:3]]
    }
    
    prompt = f"""
    Analyze this company's buying intent for B2B solutions based on multiple signals.
    Consider:
    1. Recent funding activity (if any)
    2. Employee growth (if data available)
    3. Industry news and sentiment
    4. Company maturity (revenue, size)
    5. Market position
    
    Company signals:
    {json.dumps(signals, indent=2)}
    
    Return JSON with:
    - buy_intent: "High", "Medium", or "Low"
    - confidence: 0-100 score
    - rationale: Brief explanation
    - key_signals: List of top 2-3 factors that influenced the decision
    - recommended_approach: "Aggressive", "Balanced", or "Conservative" outreach strategy
    """
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=20)
        response.raise_for_status()
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        
        try:
            parsed = json.loads(text)
            return (
                parsed.get('buy_intent'),
                parsed.get('confidence'),
                parsed.get('rationale'),
                parsed.get('key_signals', []),
                parsed.get('recommended_approach')
            )
        except Exception:
            # Fallback parsing if JSON fails
            intent_match = re.search(r'buy_intent[":\s]*([A-Za-z]+)', text)
            conf_match = re.search(r'confidence[":\s]*(\d+)', text)
            rationale_match = re.search(r'rationale[":\s]*([^\"}]+)', text)
            
            return (
                intent_match.group(1) if intent_match else None,
                int(conf_match.group(1)) if conf_match else None,
                rationale_match.group(1) if rationale_match else None,
                [],
                None
            )
    except Exception as e:
        print(f"Gemini buy intent failed: {e}")
        # Fallback: fill with default values
        return (
            "Medium",
            50,
            "Defaulted: Gemini API unavailable. Used generic signals (e.g., no recent funding, average news activity).",
            ["No Gemini response", "Fallback to default"],
            "Balanced"
        )

def search_and_enrich_companies(industry, location):
    query = f"{industry} companies in {location}"
    cse_data = enrich_google_cse(query)
    st.write("Google CSE raw data:", cse_data)  # Debug
    companies = []
    if cse_data and 'items' in cse_data:
        for item in cse_data['items']:
            name = item.get('title', '')
            link = item.get('link', '')
            companies.append({'Company Name': name, 'Company Website': link})
    brightdata_data = enrich_brightdata(query)
    st.write("Bright Data raw data:", brightdata_data)  # Debug
    if brightdata_data and 'result' in brightdata_data:
        for bd_item in brightdata_data['result']:
            name = bd_item.get('name', '')
            link = bd_item.get('website', '')
            if name and link:
                companies.append({'Company Name': name, 'Company Website': link})
    # Remove duplicates
    seen = set()
    unique_companies = []
    for c in companies:
        key = (c['Company Name'], c['Company Website'])
        if key not in seen:
            seen.add(key)
            unique_companies.append(c)
    # Enrich each company
    results = []
    try:
        nlp = spacy.load("en_core_web_lg")
    except:
        nlp = spacy.load("en_core_web_sm")
    for company in unique_companies:
        website = company.get('Company Website', '')
        # Firecrawl enrichment
        firecrawl_data = enrich_firecrawl_website(website)
        st.write(f"Firecrawl data for {website}:", firecrawl_data)  # Debug
        if firecrawl_data:
            company['firecrawl_summary'] = firecrawl_data.get('summary')
            if 'location' in firecrawl_data:
                company['HQ State'] = firecrawl_data['location']
            if 'employee_count' in firecrawl_data:
                company['Employee Count'] = firecrawl_data['employee_count']
            if 'revenue' in firecrawl_data:
                company['Revenue'] = firecrawl_data['revenue']
            # Extract phone and email from the summary text, if available
            contact_info = extract_contact_info(firecrawl_data.get('summary', ''))
            if 'phone' in contact_info:
                company['Company Phone'] = contact_info['phone']
            if 'email' in contact_info:
                company['Company Email'] = contact_info['email']
        # HubSpot enrichment
        domain = website.replace('https://', '').replace('http://', '').split('/')[0]
        if domain:
            hubspot_data = enrich_hubspot_company(domain)
            st.write(f"HubSpot data for {domain}:", hubspot_data)  # Debug
            if hubspot_data:
                company['hubspot_company_id'] = hubspot_data.get('companyId')
                props = hubspot_data.get('properties', {})
                if 'state' in props:
                    company['HQ State'] = props['state']
                if 'annualrevenue' in props:
                    company['Revenue'] = props['annualrevenue']
                if 'numberofemployees' in props:
                    company['Employee Count'] = props['numberofemployees']
        # Proxycurl enrichment (if LinkedIn found or can be constructed)
        linkedin_url = company.get('Company LinkedIn', '')
        if linkedin_url:
            proxycurl_data = enrich_linkedin_company(linkedin_url)
            st.write(f"Proxycurl data for {linkedin_url}:", proxycurl_data)  # Debug
            if proxycurl_data:
                if 'employee_count' in proxycurl_data:
                    company['Employee Count'] = proxycurl_data['employee_count']
                if 'annual_revenue' in proxycurl_data:
                    company['Revenue'] = proxycurl_data['annual_revenue']
                if 'hq_state' in proxycurl_data:
                    company['HQ State'] = proxycurl_data['hq_state']
        # Bright Data enrichment
        brightdata_data = enrich_brightdata(website)
        st.write(f"Bright Data for {website}:", brightdata_data)  # Debug
        if brightdata_data:
            if 'employee_count' in brightdata_data:
                company['Employee Count'] = brightdata_data['employee_count']
            if 'revenue' in brightdata_data:
                company['Revenue'] = brightdata_data['revenue']
            if 'location' in brightdata_data:
                company['HQ State'] = brightdata_data['location']
            if 'phone' in brightdata_data:
                company['Company Phone'] = brightdata_data['phone']
            if 'email' in brightdata_data:
                company['Company Email'] = brightdata_data['email']
        # Google CSE enrichment (if possible)
        cse_data = enrich_google_cse(company.get('Company Name', ''))
        st.write(f"Google CSE data for {company.get('Company Name', '')}:", cse_data)  # Debug
        if cse_data and 'items' in cse_data:
            for item in cse_data['items']:
                pagemap = item.get('pagemap', {})
                orgs = pagemap.get('organization', [])
                if orgs:
                    org = orgs[0]
                    if 'name' in org:
                        company['Company Name'] = org['name']
                    if 'addressregion' in org:
                        company['HQ State'] = org['addressregion']
                    if 'numberofemployees' in org:
                        company['Employee Count'] = org['numberofemployees']
                    if 'revenue' in org:
                        company['Revenue'] = org['revenue']
                    if 'industry' in org:
                        company['Industry'] = org['industry']
                metatags = pagemap.get('metatags', [])
                if metatags:
                    meta = metatags[0]
                    if 'og:locale' in meta:
                        company['Locale'] = meta['og:locale']
                    if 'og:site_name' in meta:
                        company['Site Name'] = meta['og:site_name']
                    if 'og:type' in meta and 'industry' not in company:
                        company['Industry'] = meta['og:type']
                snippet = item.get('snippet', '')
                doc = nlp(snippet)
                for ent in doc.ents:
                    if ent.label_ == 'GPE':
                        abbr = state_map.get(ent.text.lower())
                        company['HQ State'] = abbr if abbr else ent.text
                    elif ent.label_ == 'ORG':
                        company['Company Name'] = ent.text
                    elif ent.label_ == 'CARDINAL':
                        pass
                    elif ent.label_ == 'DATE':
                        year_match = re.search(r'\b(19|20)\d{2}\b', ent.text)
                        if year_match:
                            company['Year Founded'] = year_match.group(0)
                snippet = snippet.lower()
                emp_match = re.search(r'(over|more than|about|approximately)?\s?(\d{2,6})\s?(employees|staff|people|workers|team)', snippet)
                if emp_match:
                    company['Employee Count'] = emp_match.group(2)
                rev_match = re.search(r'(revenue|sales|turnover|annual sales|annual revenue|generates)[^\d]*(\$[\d,.]+)\s*(million|billion)?', snippet)
                if rev_match:
                    revenue = rev_match.group(2).replace('$', '').replace(',', '')
                    if rev_match.group(3) == 'million':
                        revenue = float(revenue) * 1_000_000
                    elif rev_match.group(3) == 'billion':
                        revenue = float(revenue) * 1_000_000_000
                    company['Revenue'] = int(revenue)
                year_match = re.search(r'(founded|established|since) in? (\d{4})', snippet)
                if year_match:
                    company['Year Founded'] = year_match.group(2)
                ind_match = re.search(r'industry:?\s*([a-zA-Z &]+)', snippet)
                if ind_match:
                    company['Industry'] = ind_match.group(1).strip()
                loc_match = re.search(r'(based in|headquartered in|offices in|operates in|hq:?|located in) ([a-zA-Z ,]+)', snippet)
                if loc_match:
                    loc = loc_match.group(2).strip()
                    abbr = state_map.get(loc.lower())
                    company['HQ State'] = abbr if abbr else loc
                for state, abbr in state_map.items():
                    if state in snippet:
                        company['HQ State'] = abbr
                # Extract phone/email from the original snippet text (case-sensitive context)
                contact_snippet = extract_contact_info(item.get('snippet', ''))
                if 'phone' in contact_snippet:
                    company['Company Phone'] = contact_snippet['phone']
                if 'email' in contact_snippet:
                    company['Company Email'] = contact_snippet['email']
                snippet = item.get('snippet', '')
                gemini_info = gemini_extract_info(snippet)
                st.write(f"Gemini extraction result for {company.get('Company Name', '')}:", gemini_info)
                if gemini_info:
                    if 'employee_count' in gemini_info:
                        company['Employee Count'] = gemini_info['employee_count']
                    if 'revenue' in gemini_info:
                        company['Revenue'] = gemini_info['revenue']
                    if 'location' in gemini_info:
                        abbr = state_map.get(gemini_info['location'].lower())
                        company['HQ State'] = abbr if abbr else gemini_info['location']
                    if 'industry' in gemini_info:
                        company['Industry'] = gemini_info['industry']
                    if 'year_founded' in gemini_info:
                        company['Year Founded'] = gemini_info['year_founded']
                    if 'linkedin_url' in gemini_info:
                        company['LinkedIn'] = gemini_info['linkedin_url']
                    if 'twitter_url' in gemini_info:
                        company['Twitter'] = gemini_info['twitter_url']
                    if 'facebook_url' in gemini_info:
                        company['Facebook'] = gemini_info['facebook_url']
                    if 'founders' in gemini_info:
                        company['Founders'] = gemini_info['founders']
                    if 'ceo' in gemini_info:
                        company['CEO'] = gemini_info['ceo']
                    if 'total_funding' in gemini_info:
                        company['Total Funding'] = gemini_info['total_funding']
                    if 'last_funding_round' in gemini_info:
                        company['Last Funding Round'] = gemini_info['last_funding_round']
                    if 'investors' in gemini_info:
                        company['Investors'] = gemini_info['investors']
        # Clean up fields for analytics and scoring
        for field in ['Employee Count', 'Revenue', 'Industry']:
            val = company.get(field)
            if val in [None, '', 'None', '000', 0]:
                company[field] = None
            else:
                if field in ['Employee Count', 'Revenue']:
                    try:
                        company[field] = int(str(val).replace(',', '').replace('$', '').strip())
                    except Exception:
                        company[field] = None
                elif field == 'Industry':
                    if str(val).lower() in ['website', 'article', 'none', '']:
                        company[field] = None
        # Use Gemini for lead scoring/justification
        score, justification = gemini_lead_scoring(company)
        st.write(f"Gemini scoring for {company.get('Company Name', '')}:", score, justification)
        if score and justification:
            company['Score'] = score
            company['Justification'] = justification
        else:
            score, justification = score_lead(company)
            company['Score'] = score
            company['Justification'] = justification

        # Buy intent classification (always executed)
        intent, confidence, rationale, signals, approach = gemini_buy_intent(company)
        if intent:
            company['Buy Intent'] = intent
            company['Intent Confidence'] = confidence
            company['Intent Rationale'] = rationale
            company['Key Signals'] = '; '.join(signals) if signals else None
            company['Recommended Approach'] = approach
        suggestions = []
        if not company.get('Company Website'):
            suggestions.append('Add website')
        company['Suggestions'] = '; '.join(suggestions) if suggestions else 'Looks good'
        results.append(company)
    result_df = pd.DataFrame(results)
    if not result_df.empty:
        st.write("## Analytics & Visualizations")
        st.write("### Score Distribution")
        st.bar_chart(result_df['Score'].value_counts())
        # Employee count histogram
        if 'Employee Count' in result_df.columns:
            try:
                emp_counts = pd.to_numeric(result_df['Employee Count'], errors='coerce').dropna()
                if not emp_counts.empty:
                    st.write("### Employee Count Distribution")
                    st.bar_chart(emp_counts.value_counts().sort_index())
            except Exception:
                pass
        # Revenue histogram
        if 'Revenue' in result_df.columns:
            try:
                revenues = pd.to_numeric(result_df['Revenue'], errors='coerce').dropna()
                if not revenues.empty:
                    st.write("### Revenue Distribution")
                    st.bar_chart(revenues.value_counts().sort_index())
            except Exception:
                pass
        # Industry/funding breakdowns
        if 'Industry' in result_df.columns:
            st.write("### Industry Breakdown")
            st.bar_chart(result_df['Industry'].value_counts())
        if 'Total Funding' in result_df.columns:
            try:
                fundings = pd.to_numeric(result_df['Total Funding'], errors='coerce').dropna()
                if not fundings.empty:
                    st.write("### Total Funding Distribution")
                    st.bar_chart(fundings.value_counts().sort_index())
            except Exception:
                pass
        # Missing data visualization
        st.write("### Missing Data Overview")
        key_fields = ['Employee Count', 'Revenue', 'Industry']
        missing_counts = result_df[key_fields].isnull().any(axis=1).value_counts()
        missing_labels = ['Complete', 'Missing Key Fields']
        missing_data = pd.Series([missing_counts.get(False, 0), missing_counts.get(True, 0)], index=missing_labels)
        st.write("#### Leads with Complete vs. Missing Key Fields")
        st.pyplot(missing_data.plot.pie(autopct='%1.0f%%', ylabel='').get_figure())
    return result_df

def generate_sales_playbook(lead):
    """
    Calls Gemini (or your LLM) to generate a sales playbook for the given lead.
    """
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY missing. Cannot generate playbook."
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    prompt = f"""
    For this company, generate:
    - The best pitch strategy (ROI, credibility, FOMO, etc.)
    - 3 icebreakers using their latest news, tweets, or funding
    - Objection-handling guide (top 2 objections and responses)
    - Best time to reach out (timezone, psychographic guess)
    Company data: {json.dumps(lead)}
    """
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=20)
        response.raise_for_status()
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        return text
    except Exception as e:
        return f"Error generating playbook: {e}"

# Add new utility functions for contact extraction and buy intent scoring

def extract_contact_info(text: str) -> dict:
    """Extract a phone number and email address from a block of text."""
    info = {}
    if not text:
        return info
    # Email pattern
    email_match = re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text)
    if email_match:
        info['email'] = email_match.group(0)
    # Phone pattern (very loose, grabs international formats too)
    phone_match = re.search(r'(\+?\d[\d\-().\s]{7,}\d)', text)
    if phone_match:
        info['phone'] = phone_match.group(1)
    return info

if submitted:
    with st.spinner("Searching and enriching companies..."):
        result_df = search_and_enrich_companies(industry, location)
    # Removed the Red/Yellow/Green filter (it was unreliable); always show the full list
    filter_state = st.text_input("Filter by State (optional, e.g., CA)")
    filtered_df = result_df.copy()
    if filter_state and 'HQ State' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['HQ State'] == filter_state]
    st.write("### Enriched & Scored Companies", filtered_df)
    def highlight_score(row):
        color = {'Green': '#d4edda', 'Yellow': '#fff3cd', 'Red': '#f8d7da'}.get(row['Score'], '')
        return [f'background-color: {color}' if i == 'Score' else '' for i in row.index]
    st.dataframe(filtered_df.style.apply(highlight_score, axis=1))
    st.download_button("Export to CSV", filtered_df.to_csv(index=False), file_name="caprae_leads.csv", mime="text/csv")
    if st.button("Export to Google Sheets"):
        url = export_to_gsheet(filtered_df)
        if url:
            st.success(f"Exported to Google Sheets: {url}")
    for idx, row in filtered_df.iterrows():
        if st.button(f"Generate Playbook for {row['Company Name']}", key=f"playbook_{idx}"):
            playbook = generate_sales_playbook(row.to_dict())
            st.markdown(f"**Sales Playbook for {row['Company Name']}**\n\n{playbook}")