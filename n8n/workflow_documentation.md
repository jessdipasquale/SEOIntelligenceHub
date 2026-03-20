# n8n Workflow Documentation — SEO Intelligence Hub

**Workflow name:** SEO Intelligence Hub — Competitive Analysis Scheduler
**File:** `n8n/workflow.json`
**Use Case:** UC1 — Automated SERP Competitive Intelligence

---

## 1. What This Workflow Does

Every 3 days, this workflow automatically:
1. Loads the keyword watchlist (list of keywords to monitor for each client)
2. For each keyword, fetches the top-10 Google SERP results via SerpApi
3. Sends the competitor titles and snippets to Claude for gap analysis
4. Formats a branded HTML report
5. Sends the report by email (SendGrid) and posts a summary to Slack

**Time saved:** An analyst would spend 20–40 minutes per keyword manually. This workflow processes each keyword in ~30 seconds with no human involvement.

---

## 2. Workflow Architecture

```
[Scheduler: Every 3 days]
         │
         ▼
[Load Keyword Watchlist]  ← JSON file / Google Sheets / Airtable
         │
         ▼
[Split into batches]  ← 1 keyword at a time
         │
         ▼
[SerpApi: Fetch top-10 SERP]  ← returns URLs, titles, snippets
         │
         ▼
[Extract competitor data]  ← JavaScript node: clean & format
         │
         ▼
[Claude Haiku: Gap Analysis]  ← LLM call ~$0.001
         │
         ▼
[Format HTML Report]  ← branded email template
    ┌────┴────┐
    ▼         ▼
[Send Email]  [Slack notification]
```

---

## 3. Node Configuration

### Node 1 — Schedule Trigger
- **Type:** Schedule Trigger
- **Frequency:** Every 3 days
- **When to change:** Adjust to weekly for lighter monitoring, daily for high-competition keywords

### Node 2 — Load Keyword Watchlist
- **Type:** HTTP Request (GET)
- **What it fetches:** A JSON array of keywords to monitor
- **Example JSON format:**
```json
[
  {"keyword": "best crm software", "client": "ClientA"},
  {"keyword": "email marketing tools", "client": "ClientA"},
  {"keyword": "seo audit tool", "client": "ClientB"}
]
```
- **Production alternative:** Replace with Google Sheets node or Airtable node for easier client management

### Node 3 — Split Keywords
- **Type:** Split in Batches (size: 1)
- **Purpose:** Processes one keyword per iteration to respect SerpApi's rate limits and ensure clean error handling

### Node 4 — Fetch SERP Results (SerpApi)
- **Type:** HTTP Request (GET)
- **API:** `https://serpapi.com/search`
- **Parameters:** `engine=google`, `q={keyword}`, `num=10`
- **Free tier:** 100 searches/month
- **Environment variable needed:** `SERP_API_KEY`

### Node 5 — Extract Competitor Data
- **Type:** Code (JavaScript)
- **What it does:** Parses SerpApi response, extracts top-10 organic results, formats for LLM input
- **Output:** keyword, competitors array, formatted summary string

### Node 6 — Claude Gap Analysis
- **Type:** HTTP Request (POST to Anthropic API)
- **Model:** `claude-haiku-4-5-20251001` (fast, cost-efficient)
- **Cost:** ~$0.001 per keyword analysis
- **Environment variable needed:** `ANTHROPIC_API_KEY`
- **Prompt:** Grounded in competitor titles/snippets — cannot hallucinate

### Node 7 — Format HTML Report
- **Type:** Code (JavaScript)
- **What it does:** Builds a branded HTML email with gap analysis + competitor table

### Node 8 — Send Email (SendGrid)
- **Type:** Email Send
- **Provider:** SendGrid (free tier: 100 emails/day)
- **Credential:** Configure SendGrid API key in n8n Credentials
- **Environment variable needed:** `REPORT_RECIPIENT_EMAIL`

### Node 9 — Slack Notification
- **Type:** Slack
- **Purpose:** Posts a 3-line summary to the team channel when each report is ready
- **Environment variable needed:** `SLACK_CHANNEL_ID`

---

## 4. Setup Instructions

### Step 1 — Import the workflow
1. Open n8n (cloud: app.n8n.cloud, or self-hosted)
2. New Workflow → Import from file → select `n8n/workflow.json`

### Step 2 — Configure credentials
In n8n Settings → Credentials, add:
- **SerpApi:** `SERP_API_KEY` from serpapi.com (free: 100 searches/month)
- **Anthropic:** `ANTHROPIC_API_KEY` from console.anthropic.com
- **SendGrid:** API key from sendgrid.com (free: 100 emails/day)
- **Slack:** OAuth token for your workspace

### Step 3 — Set up environment variables
In n8n Settings → Variables:
```
SERP_API_KEY=your_serpapi_key
ANTHROPIC_API_KEY=your_anthropic_key
REPORT_RECIPIENT_EMAIL=team@your-agency.com
SLACK_CHANNEL_ID=C0XXXXXXX
```

### Step 4 — Update keyword watchlist
Replace the static URL in Node 2 with your keyword list file.
For a production setup, connect to a Google Sheet with client keywords.

### Step 5 — Test manually
1. Click "Test Workflow" in n8n
2. Check the execution log for each node
3. Verify email is received and Slack message appears
4. Then activate the workflow to enable the scheduler

---

## 5. Cost Analysis

| Resource | Cost |
|---|---|
| SerpApi (100 searches/month free) | €0 |
| Claude Haiku per keyword analysis | ~€0.001 |
| 200 keywords analyzed per month | ~€0.20 |
| SendGrid (100 emails/day free) | €0 |
| n8n cloud (free tier) | €0 |
| **Total monthly cost** | **~€0.20** |

---

## 6. Error Handling

The workflow is designed to be resilient:
- If SerpApi returns no results for a keyword → the keyword is skipped and logged
- If Claude returns an error → a fallback message is included in the report
- If email sending fails → Slack notification still fires as a backup alert
- If Slack fails → email is still sent

For production, add an error workflow in n8n: Settings → Error Workflow → notify the admin on any failure.

---

## 7. Extending the Workflow (v2 roadmap)

| Extension | Effort | Value |
|---|---|---|
| Add rank tracking (compare positions week-over-week) | Medium | High |
| Add backlink check for top competitor | Medium | Medium |
| Generate full content brief (not just gaps) | Low (prompt change) | High |
| Multi-language support (hreflang keywords) | Medium | Medium |
| Auto-create Notion page with report | Low | Medium |
