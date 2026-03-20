# Dashboard Documentation — SEO Intelligence Hub

**Tool:** Tableau (replacing PowerBI as per project config)
**File:** `dashboard/seo_intelligence_hub.twbx`
**Data sources:** `data/processed/` (4 clean CSVs)
**Date:** 2026-03-19

---

## 1. Dashboard Philosophy

This dashboard follows the **Communication Layer** principle:
- Every visual answers a specific business question Chleo would ask
- No chart exists for aesthetics — each one drives a decision
- The layout follows the **F-pattern** (most important info top-left to top-right)
- Color encoding is consistent: 🔴 Red = problem/drop, 🟢 Green = opportunity/improvement, 🔵 Blue = neutral metric

---

## 2. Dashboard Structure: 3 Views (1 per Use Case)

---

### View 1 — Competitive Intelligence Overview
**Data source:** `serp_clean.csv`
**Business question:** *"Which competitors dominate our target keywords, and where are our content gaps?"*

#### Charts

**A. Domain Frequency in Top 10 (Bar Chart — horizontal)**
- X-axis: count of appearances in top-10 SERP positions
- Y-axis: domain name
- Color: shade intensity = avg position (darker = higher ranked)
- Filter: selectable by keyword or keyword group
- Business insight: Instantly shows which domains own the SERP for your keyword set

**B. SERP Position Distribution (Box Plot)**
- One box per top-5 domain
- Shows median position, IQR, outliers
- Business insight: Is a competitor consistently at position 1 or just sometimes?

**C. Keyword Coverage Heatmap**
- Rows: top 20 keywords
- Columns: top 10 domains
- Cell: position number (1–10), color-coded (1=dark green → 10=light green, blank=not ranking)
- Business insight: Identifies keyword clusters where multiple competitors are present but the client is absent

**D. KPI Cards (top row)**
- Total keywords monitored
- Average competitor position
- # keywords where no top-3 slot is taken by a known competitor (= opportunity gap)

---

### View 2 — Keyword Opportunity Matrix
**Data source:** `keywords_clean.csv` + `gsc_performance_clean.csv`
**Business question:** *"Which keywords should we prioritize for new content, and which ones just need optimization?"*

#### Charts

**A. Opportunity Scatter Plot (main visual)**
- X-axis: Keyword Difficulty (0–100)
- Y-axis: Search Volume
- Bubble size: CPC (proxy for commercial value)
- Color: Search Intent (informational=blue, commercial=orange, transactional=red, navigational=grey)
- Quadrant lines at Difficulty=40, Volume=500
- **Top-left quadrant** (low difficulty, high volume) = "Quick Wins"
- Business insight: Chleo sees at a glance where to invest content effort

**B. Intent Distribution (Donut Chart)**
- Segments: % of keywords per intent type
- Business insight: If 60% of keywords are informational and the client wants sales, there's a strategy misalignment

**C. Priority Score Ranking (Bar Chart — top 20)**
- X-axis: Priority Score = Volume × (1 - Difficulty/100)
- Y-axis: Keyword
- Color: Intent type
- Business insight: Top 20 keywords to action first, objectively ranked

**D. CTR Opportunity (Scatter Plot)**
- X-axis: Avg Position (from GSC data)
- Y-axis: Impressions
- Color: CTR (red=low, green=high)
- Business insight: High impressions + low CTR at position 3–5 = "optimize title tag, don't write new content"

---

### View 3 — Rank Monitoring & Alerts
**Data source:** `rank_tracking_clean.csv`
**Business question:** *"Are our rankings stable? Where are we dropping, and how fast?"*

#### Charts

**A. Rank Trend Lines (Line Chart)**
- X-axis: Date (weekly)
- Y-axis: SERP Position (inverted — position 1 at top)
- One line per keyword (max 10 on screen, filterable)
- Red band: positions 11–20 (page 2 — "danger zone")
- Business insight: Visual trend of ranking trajectory

**B. Rank Drop Alerts Table**
- Columns: Keyword | Previous Rank | Current Rank | Change | Drop Severity
- Color: 🔴 Drop >5, 🟡 Drop 2–5, 🟢 Stable/Improved
- Sorted by: severity descending
- Business insight: The "morning dashboard" — what needs attention today

**C. Volatility Score (KPI Cards)**
- % of keywords that moved ±3 or more positions this week
- # of keywords that entered page 2 this week
- # of keywords that moved to page 1 this week

**D. Competitor Rank Changes (Grouped Bar)**
- For top-5 competitors: bars showing avg rank improvement/decline vs prior week
- Business insight: If a competitor improved 2 positions on average, they may have published new content or earned links

---

## 3. Tableau Setup Instructions

### Step 1 — Connect Data Sources
1. Open Tableau Desktop
2. Connect → Text File → select `data/processed/serp_clean.csv`
3. Repeat for all 4 clean CSVs
4. Create relationships between datasets:
   - `serp_clean` JOIN `keywords_clean` ON `query = keyword`
   - `gsc_performance_clean` JOIN `keywords_clean` ON `query = keyword`

### Step 2 — Create Calculated Fields
In Tableau, create these calculated fields:

```
Priority Score = [search_volume] * (1 - [difficulty] / 100)

Rank Change Color =
  IF [rank_change] < -5 THEN "Critical Drop"
  ELSEIF [rank_change] < -2 THEN "Minor Drop"
  ELSEIF [rank_change] > 2 THEN "Improvement"
  ELSE "Stable"
  END

Opportunity Label =
  IF [difficulty] < 40 AND [search_volume] > 500 THEN "Quick Win"
  ELSEIF [difficulty] < 60 AND [search_volume] > 1000 THEN "Medium Term"
  ELSE "Long Term"
  END
```

### Step 3 — Dashboard Layout
1. Create each chart as a separate Sheet (Sheet 1 = SERP Overview, etc.)
2. New Dashboard → set size to 1400 × 900px
3. Drag sheets into layout following the wireframe below
4. Add filters: Keyword selector (multi-select), Date range, Intent type
5. Enable filter actions: clicking a domain in View 1 filters View 3

---

## 4. ASCII Wireframe

```
┌─────────────────────────────────────────────────────────────────────┐
│  SEO INTELLIGENCE HUB  │  [Filter: Keyword Group ▼] [Date Range ▼] │
├─────────────────────────────────────────────────────────────────────┤
│  [TAB: Competitive Intel] [TAB: Keyword Opportunity] [TAB: Ranks]   │
├───────────────────────────┬─────────────────────────────────────────┤
│                           │  KPI CARDS                              │
│   DOMAIN FREQUENCY        │  [Total KW] [Avg Pos] [Gap Opps]       │
│   IN TOP-10               ├─────────────────────────────────────────┤
│   (Horizontal Bar)        │                                         │
│                           │   KEYWORD COVERAGE HEATMAP              │
│                           │   (Keywords × Domains)                  │
│                           │                                         │
├───────────────────────────┴─────────────────────────────────────────┤
│                                                                     │
│   SERP POSITION DISTRIBUTION PER DOMAIN (Box Plot)                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Communication Layer Checklist

- [ ] Every chart has a title phrased as a question ("Which domains dominate?")
- [ ] No chart requires more than 5 seconds to interpret
- [ ] Color legend is always visible
- [ ] Filters are labeled in plain language, not technical terms
- [ ] KPI cards are at the top (scannability)
- [ ] No more than 7 charts per view (cognitive load limit)
