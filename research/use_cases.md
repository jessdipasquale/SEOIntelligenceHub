# Use Case Proposals: SEO Intelligence Hub

**Project:** SEO Intelligence Hub
**Sector:** Digital Marketing / SEO Agency
**Company Size:** Small (10–50 employees)

---

## Overview

Three use cases have been selected for Chleo's agency based on:
1. **Highest ROI** relative to implementation complexity
2. **Direct relevance** to the agency's daily workflow
3. **Demonstrability** — each produces a tangible, client-presentable output
4. **Fit for small company** — solvable with free-tier APIs and minimal infrastructure

---

## Use Case 1 — SEO Competitive Intelligence Agent

### Problem
Manual SERP analysis per keyword takes 20–40 minutes: open top-10 results, read content, note H1/H2 structures, extract covered topics, identify gaps vs. client's existing content, formulate recommendations. For an agency monitoring 200+ keywords across 28 clients, this is unsustainable. It happens quarterly at best — meaning clients receive outdated competitive intelligence.

### Solution
An autonomous agent that, given a target keyword:
1. Fetches top-10 SERP results via **SerpApi**
2. Scrapes each URL and extracts heading structure (H1/H2/H3) + body content via **BeautifulSoup**
3. Embeds competitor content in **Pinecone** for semantic comparison
4. Runs gap analysis with an **LLM (Claude/GPT-4o)** — identifying topics covered by competitors but absent from the client's page
5. Outputs a structured report: topic gaps ranked by competitor frequency, recommended content additions, H2 structure suggestion

Delivered via **Gradio UI** and **automated email every 3 days via n8n**.

### Value Delivered
| Metric | Before | After |
|---|---|---|
| Time per keyword analysis | 20–40 min | <5 min |
| Analysis frequency | Quarterly | Weekly |
| Keywords monitored simultaneously | 10–20 | 200+ |
| Senior analyst hours freed/month | ~60h | ~5h (QA only) |

### Dataset Used
- `google_serp_data.csv` — simulates SerpApi output (query, position, domain, title, snippet, URL)

### Technical Components
- **LangGraph** for multi-step workflow orchestration
- **SerpApi** for live SERP data (100 free searches/month)
- **BeautifulSoup + requests** for content extraction
- **Pinecone** for vector storage and semantic similarity
- **Claude claude-haiku-4-5-20251001 / GPT-4o-mini** for gap analysis (cost-optimized)
- **n8n** for scheduling and email delivery
- **LangSmith** for monitoring and transparency

---

## Use Case 2 — Keyword Clustering & Intent Classification

### Problem
After any keyword research session, an analyst exports hundreds or thousands of keywords from SEMrush or Ahrefs. Grouping them into semantic clusters and classifying by search intent (informational, navigational, transactional, commercial investigation) is done manually in Excel — typically using string matching and personal judgment. The process is inconsistent across team members, takes 2–3 hours per client, and the output quality degrades with volume.

### Solution
A Python script + LLM pipeline that:
1. Accepts a CSV of raw keywords (keyword, search volume, difficulty, CPC)
2. Generates embeddings for each keyword via **OpenAI text-embedding-3-small**
3. Clusters keywords semantically using **K-Means** or **HDBSCAN**
4. Classifies each cluster's dominant intent via **LLM prompt** (few-shot classification)
5. Outputs a structured CSV: keyword, cluster_label, intent, priority_score (volume × (1 - difficulty/100))

The output feeds directly into the **Tableau dashboard** as a content prioritization matrix.

### Value Delivered
| Metric | Before | After |
|---|---|---|
| Time for keyword classification (500 kw) | 2–3 hours | <10 minutes |
| Consistency across analysts | Variable | Standardized |
| Intent accuracy | ~75% (manual) | ~88% (AI + embeddings) |
| Content strategy coverage | 30–40% of clusters actioned | 80%+ (prioritized backlog) |

### Dataset Used
- `seo_keyword_research.csv` — keyword, search_volume, difficulty, CPC, intent (ground truth for evaluation)
- `ai_google_keyword_performance.csv` — real query performance data for validation

### Technical Components
- **OpenAI text-embedding-3-small** for keyword embeddings
- **scikit-learn** (K-Means) or **hdbscan** for clustering
- **Claude / GPT-4o-mini** for intent classification (few-shot)
- **pandas + numpy** for data processing
- **LangSmith** for logging classification calls

---

## Use Case 3 — Rank Drop Alert & Contextual Diagnosis

### Problem
Rank drops are discovered reactively. A client reports a traffic drop, the team opens GSC, compares date ranges, finds affected keywords, then manually investigates: Was there a Google algorithm update? Did a new competitor appear? Is there a cannibalization issue? This investigation takes 1–2 hours per incident and delays the client response window, damaging trust.

### Solution
An automated monitoring pipeline that:
1. Ingests weekly SERP position data per keyword (from dataset or live via SerpApi)
2. Detects significant drops: **position change >3 ranks** OR **CTR drop >20%** week-over-week
3. For each flagged keyword, calls an **LLM with context**: current SERP, competitor changes, historical trend, known algorithm update dates
4. Generates a **root cause hypothesis** (e.g., "New competitor [domain.com] entered top-3. Their content covers [topic X] which your page lacks.")
5. Sends an **alert via n8n** to Slack + email with the diagnosis and recommended action

### Value Delivered
| Metric | Before | After |
|---|---|---|
| Time to detect rank drop | 1–7 days (reactive) | <24 hours (proactive) |
| Investigation time per incident | 1–2 hours | 15 minutes (review AI diagnosis) |
| Client response time | 2–5 days | Same day |
| Client churn due to missed drops | ~10% annual | Target: <3% |

### Dataset Used
- `serp_datasets.csv` — keyword, rank, domain, date (time-series for drop detection)

### Technical Components
- **pandas** for time-series anomaly detection (rolling average, delta threshold)
- **Claude / GPT-4o-mini** for contextual root cause analysis
- **n8n** for alert routing (Slack webhook + SendGrid email)
- **LangSmith** for monitoring diagnosis quality

---

## Use Case Prioritization Summary

| Use Case | Complexity | ROI | MVP Priority |
|---|---|---|---|
| UC1 — Competitive Intelligence Agent | High | Very High | ✅ Core MVP |
| UC2 — Keyword Clustering & Intent | Medium | High | ✅ Core MVP |
| UC3 — Rank Drop Alert | Medium | High | ✅ Core MVP |

All three use cases are included in the MVP. They share infrastructure (LangSmith, n8n, Python environment) and can be demonstrated independently in a single meeting with Chleo.

---

## Justification for Company Size

These use cases are specifically calibrated for a **small agency (10–50 employees)**:

- **Cost:** Total API cost is <€15/month at the agency's scale. No enterprise contracts required.
- **Infrastructure:** Zero-server architecture (n8n cloud, Pinecone free tier, SerpApi free tier). No DevOps needed.
- **Adoption:** Each use case produces a self-explanatory output (report, CSV, Slack alert) that the team can start using without retraining.
- **Maintenance:** LangSmith monitoring means the owner can verify the AI is working correctly without reading code.
