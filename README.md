# Project Demo Video

[Watch the detailed explanation of the working of the website and product](https://youtu.be/GY-Mxgnl0-E?si=-MWEBv44a3LLNgYr)

# Caprae Lead QA Tool

## Overview
The Caprae Lead QA Tool discovers, enriches, and qualifies B2B companies so sales teams can prioritize high-impact leads faster.

> “Great Founders Working with Great Founders.”

---

### Core Capabilities
1. **Company Discovery** – Uses Google CSE & Bright Data to find target companies by *industry* & *location*.
2. **Data Enrichment** – Firecrawl, HubSpot, Proxycurl, and Bright Data APIs extract employee size, revenue, HQ, funding stage, etc.
3. **LLM Insights** – Gemini Pro scores each lead (Green/Yellow/Red) and estimates Buy-Intent (High/Medium/Low) with rationale.
4. **Contact Extraction** – Regex + scraping parses emails & phone numbers from web snippets.
5. **Visual Analytics** – Interactive Streamlit charts: score breakdown, industry histograms, missing-data pie, and more.
6. **Sales Playbook Generator** – One-click Gemini prompt returns custom pitch, icebreaker, objections, and ideal contact timing.
7. **Exports** – Download as CSV or push directly to Google Sheets.

---

## Setup Instructions

```bash
# Clone the repo
git clone https://github.com/caprae/caprae-new.git
cd caprae_new

# (optional) create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add your API keys
cp .env.example .env
nano .env  # or use any editor to paste in your keys

# Run the app
streamlit run app.py  # defaults to http://localhost:8501
````

---

### Required Environment Variables

```
GEMINI_API_KEY=
GOOGLE_CSE_API_KEY=
GOOGLE_CSE_CX_ID=
BRIGHTDATA_API_KEY=
FIRECRAWL_API_KEY=
PROXYCURL_API_KEY=
HUBSPOT_API_KEY=
```

→ Save these in `.env` or export them directly into your terminal session.

---

## Project Structure

```
├── app.py              # Streamlit UI and orchestration
├── api_clients.py      # Modular wrappers for external APIs
├── qa_logic.py         # Heuristic fallback scoring logic
├── README.md           # ← this file
├── REPORT.md           # One-page technical report (PDF/Markdown)
├── requirements.txt    # Python dependencies
└── .env.example        # Template for environment variables


---
```

## Quick Demo

1. Launch the app in browser.
2. Enter *Industry* (e.g., “fin-tech”) and *Location* (e.g., “California”).
3. Click **Search Companies**.
4. Review enriched leads with AI-powered scoring.
5. Click **Generate Playbook** to get a customized outreach strategy.
6. Export data to CSV or Google Sheets with one click.

---

## License

**Proprietary – for internal use only by Caprae Capital Partners.**
See `LICENSE` file for details.

---

## Tip for Devs

If you're working locally, include this in `app.py` for env loading:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

