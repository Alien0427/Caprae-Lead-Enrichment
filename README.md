# Caprae Lead QA Tool

## Overview
Caprae Lead QA Tool discovers, enriches, and qualifies B2B companies so sales teams can prioritize high-impact leads.  
"Great Founders Working with Great Founders."

### Core Capabilities
1. **Company Discovery** – Google CSE & Bright Data scrape candidate companies by *industry* & *location*.
2. **Data Enrichment** – Firecrawl, HubSpot, Proxycurl, Bright Data APIs provide employees, revenue, HQ, etc.
3. **LLM Insights** – Google Gemini-pro scores lead fit (Green/Yellow/Red) and Buy-Intent (High/Medium/Low) with rationale.
4. **Contact Extraction** – Regex over website summaries for phone & email.
5. **Visual Analytics** – Streamlit charts on scores, revenue, employee counts, industries, missing-data heatmap.
6. **Sales Playbook** – 1-click Gemini prompt returns pitch strategy, ice-breakers, objections, best contact time.
7. **Exports** – CSV download & Google-Sheets push.

---
## Setup
```bash
# clone repo
$ git clone https://github.com/<your-org>/caprae-lead-qa.git
$ cd caprae-lead-qa

# (optional) virtual env
$ python -m venv venv
$ source venv/bin/activate  # Windows: venv\Scripts\activate

# install deps
$ pip install -r requirements.txt

# add env vars
$ cp .env.example .env
$ nano .env  # paste your API keys

# run
$ streamlit run app.py  # default on :8501
```
If :8501 is busy:
```bash
streamlit run app.py --server.port 8502
```

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
*(Create `.env` or export vars in shell.)*

---
## Project Structure
```
├── app.py              # Streamlit UI + orchestration
├── api_clients.py      # Thin wrappers for external APIs
├── qa_logic.py         # Heuristic fallback scoring
├── README.md           # ← you are here
├── REPORT.md           # 1-page technical report
├── requirements.txt    # Python deps
└── .env.example        # list of needed env keys
```

---
## Quick Demo
1. Open the web app.
2. Enter *Industry* (e.g., "fin-tech"), *Location* (e.g., "California"), press **Search Companies**.
3. Scroll the results table; click **Generate Playbook** for any row.
4. Export via **CSV** or **Google Sheets**.

---


---
## License
Proprietary – for internal use only by **Caprae Capital Partners**. See `LICENSE` file.

from dotenv import load_dotenv
load_dotenv()


