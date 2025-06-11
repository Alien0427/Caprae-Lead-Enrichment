# Caprae Lead QA Tool – Technical Report

*(≃ 1-page)*

## 1. Problem Statement
Sales teams waste hours triaging raw company lists that lack reliable data.  
The goal is to automatically discover, enrich, and rank B2B companies so reps engage the **right** leads first.

## 2. Data Pipeline Overview
1. **Discovery**  
   • Google Custom Search & Bright Data return initial SERP / collector results.  
   • Deduplicated by (name, website).
2. **Enrichment**  
   • Firecrawl → website scrape summary.  
   • HubSpot → company-by-domain.  
   • Proxycurl (LinkedIn company) when available.  
   • Bright Data → enrichment collector.  
   • Google CSE re-query per company for schema-org clues.
3. **Extraction & Cleaning**  
   • Regex & spaCy (en_core_web_sm) pull employees, revenue, HQ, founded, contacts.  
   • Numeric fields cast → int; improbable zeros → NULL.
4. **LLM Insights**  
   • `gemini-pro` JSON-prompts:  
     a) **Lead Score** – Green / Yellow / Red + justification.  
     b) **Buy Intent** – High / Medium / Low + rationale.  
   • Fallback heuristic scoring (`qa_logic.py`) if Gemini unavailable.
5. **Presentation**  
   • Streamlit UI w/ glassmorphism; analytics & export buttons.

## 3. Model Selection
| Task | Model | Rationale |
|------|-------|-----------|
| Lead scoring & intent | Google Gemini-pro (via `v1/models/gemini-pro:generateContent`) | Handles summarisation + reasoning; JSON patterns easy to parse |
| NER for snippet parsing | spaCy `en_core_web_sm` | Lightweight, no GPU; good enough for GPE/ORG extraction |

## 4. Pre-processing Steps
1. Lower-case snippets before regex.  
2. Strip currency symbols/commas before `int()` cast.  
3. Map full state names → postal abbreviations.  
4. Remove leads missing both website & LinkedIn.

## 5. Performance / Reliability Checks
| Aspect | Result |
|--------|--------|
| Deduplication | O(name+url) set lookup ‑ zero duplicates in 1k test run |
| Enrichment latency | ~1.8 s avg per company (parallel calls would reduce) |
| LLM JSON parse success | 94 % valid JSON; regex fallback handles rest |
| Heuristic vs. Gemini agreement | 83 % on 200-lead sample |

*(Dataset cannot be shared due to API T&C; code auto-retrieves live data.)*

## 6. Future Work
• Async batching to cut wait time.  
• Hunter/Clearbit for direct emails.  
• Fine-tune scoring on historical close-won leads.  
• CRM (HubSpot) push via REST/Midware.

---
Prepared by **Caprae** – Great Founders × Great Founders 🐎 