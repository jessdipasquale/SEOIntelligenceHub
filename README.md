# SEO Intelligence Hub

**AI Consulting Project — Module 5**
**Sector:** Digital Marketing / SEO Agency
**Company Size:** Small (10–50 employees)
**Student:** Jessica Di Pasquale

---

## Project Summary

The SEO Intelligence Hub is an AI-powered automation system for small SEO agencies. It automates three high-value workflows that currently consume ~220 hours/month of manual analyst time:

| Use Case | What it does | Time saved |
|---|---|---|
| UC1 — Competitive Intelligence | Scrapes top-10 SERP competitors, runs LLM gap analysis, sends report every 3 days | ~156h/month |
| UC2 — Keyword Clustering | Clusters keyword exports by topic and intent using embeddings + K-Means | ~39h/month |
| UC3 — Rank Drop Alert | Detects rank drops and generates root cause hypotheses | ~18h/month |

**Total ROI:** ~€10,400/month in saved labor at a running cost of ~€251/month.

---

## Project Structure

```
seo-intelligence-hub/
├── data/
│   ├── raw/                    ← Place Kaggle CSV files here
│   └── processed/              ← Cleaned outputs from explore_and_clean.py
│   └── explore_and_clean.py    ← Data cleaning script
├── research/
│   ├── sector_research.md      ← Industry analysis & data sources
│   ├── opportunities_risks.md  ← AI opportunity & risk mapping
│   └── use_cases.md            ← 3 use case proposals with justification
├── dashboard/
│   └── dashboard_documentation.md  ← Tableau dashboard guide + wireframe
├── n8n/
│   ├── workflow.json           ← Import directly into n8n
│   └── workflow_documentation.md
├── agent/
│   ├── agent.py                ← LangGraph competitive intelligence agent (UC1)
│   └── tools.py                ← Keyword clustering + rank drop tools (UC2, UC3)
├── langsmith/
│   ├── dataset_creation.py     ← Creates 15-example evaluation dataset
│   └── monitoring_setup.py     ← Runs evaluation + explains monitoring to Chleo
├── cost_estimation/
│   ├── cost_analysis.md        ← Full ROI calculation
│   └── timeline_estimate.md    ← 12-week implementation plan
├── requirements.txt
├── .env.example                ← Copy to .env and fill in your API keys
└── README.md
```

---

## Datasets Used

| Dataset | Source | Use Case |
|---|---|---|
| Google SERP Search Data | [Kaggle — polartech](https://www.kaggle.com/datasets/polartech/google-serpsearch-engine-result-seo-search-data) | UC1 |
| SEO Keyword Research | [Kaggle — sheryshisingh](https://www.kaggle.com/datasets/sheryshisingh/seo-keyword-research) | UC2 |
| AI Google Search Keyword Performance | [Kaggle — devraai](https://www.kaggle.com/datasets/devraai/ai-google-search-keyword-performance) | UC2 + Dashboard |
| SERP Datasets | [Kaggle — eliasdabbas](https://www.kaggle.com/datasets/eliasdabbas/serp-datasets) | UC3 |

Download all four CSVs and place them in `data/raw/` with these names:
- `google_serp_data.csv`
- `seo_keyword_research.csv`
- `ai_keyword_performance.csv`
- `serp_datasets.csv`

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/your-username/seo-intelligence-hub
cd seo-intelligence-hub
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
# Edit .env with your keys
```

Required keys:
- `ANTHROPIC_API_KEY` — from console.anthropic.com
- `OPENAI_API_KEY` — from platform.openai.com (for embeddings)
- `SERP_API_KEY` — from serpapi.com (100 free/month)
- `LANGCHAIN_API_KEY` — from smith.langchain.com

### 3. Clean the data

```bash
python data/explore_and_clean.py
```

### 4. Build the Tableau dashboard

Open Tableau → Connect to Text File → `data/processed/serp_clean.csv`
See `dashboard/dashboard_documentation.md` for full setup instructions.

### 5. Set up LangSmith monitoring

```bash
python langsmith/dataset_creation.py
python langsmith/monitoring_setup.py
```

View results at: https://smith.langchain.com → Projects → seo-intelligence-hub

### 6. Import n8n workflow

1. Open n8n cloud (app.n8n.cloud)
2. New Workflow → Import → select `n8n/workflow.json`
3. Configure credentials (SerpApi, Anthropic, SendGrid, Slack)
4. Test manually, then activate the scheduler

### 7. Run the agent

```bash
python agent/agent.py --keyword "best crm software" --client-domain "example.com"
```

---

## Technical Stack

| Layer | Tool | Purpose |
|---|---|---|
| Agent framework | LangGraph | Multi-step workflow with state management |
| LLM | Claude Haiku (Anthropic) | Gap analysis, intent classification, root cause |
| Embeddings | OpenAI text-embedding-3-small | Keyword semantic clustering |
| SERP data | SerpApi | Live Google search results |
| Scraping | BeautifulSoup + requests | Competitor content extraction |
| Vector store | Pinecone | Semantic similarity search |
| Dashboard | Tableau | BI visualization (replaces PowerBI) |
| Automation | n8n | Scheduler + email + Slack |
| Monitoring | LangSmith | AI transparency + evaluation |
| Data processing | pandas, numpy, scikit-learn | Cleaning, clustering, anomaly detection |

---

## Key Results (Projected)

- 213 hours/month freed from manual analysis
- ~€10,400/month net benefit
- Payback period: < 1 week
- LangSmith hallucination score target: >90%
- Report delivery: 100% automated, every 3 days

---

## License

For educational purposes only — AI Consulting Bootcamp, Module 5 Project.
