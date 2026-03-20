# Project Documentation — SEO Intelligence Hub

**Project:** SEO Intelligence Hub
**Module:** Module 5 — AI Strategy & Business Impact
**Student:** Jessica Di Pasquale

---

## 1. Use Case Description

For this project I chose to work in the digital marketing / SEO sector, specifically for a small boutique SEO agency. The fictional client, Chleo, is the CEO of a 22-person agency managing 28 active clients with around €1.2M in annual revenue. Her team spends between 180 and 240 hours per month doing manual, repetitive analysis work — reviewing competitor SERP results, classifying keywords, and investigating rank drops after a client's traffic decreases.

Chleo's main concern about AI is transparency. She doesn't trust it because she doesn't understand how it works, and she worries it might "make things up." This made her an interesting client for this project because the goal wasn't just to build something useful — it was to build something she could actually trust and verify.

The core problem is a capacity bottleneck. The agency can't take on more clients without hiring, because analysts are spending most of their time on tasks that are repetitive and don't require senior-level thinking. Competitive analysis happens quarterly instead of weekly because there simply isn't time. Rank drops are discovered reactively — usually when a client calls to ask why their traffic dropped — which damages trust.

The three main stakeholders are Chleo herself (who needs to see ROI and transparency), the five SEO analysts (who need tools that save them time without reducing quality), and the three account managers (who receive the reports and communicate findings to clients). The 28 clients are indirect beneficiaries.

I chose this use case because SEO analysis is a high-volume, pattern-matching task — which is exactly what LLMs are good at. The inputs are structured (headings, keyword data, position numbers) and the outputs are directly actionable. The ROI is also easy to calculate and communicate, which is important when presenting to a skeptical CEO.

---

## 2. Dataset Justification

I used four public datasets from Kaggle, all chosen because they mirror the actual data an SEO agency deals with every week.

The first dataset (`GoogleRankProductDaily_2022-04-21` by polartech, ~96,000 rows) contains Google SERP rankings including keyword, position, domain, title, and date. This replicates the kind of data you'd get from SerpApi in production, and it's the core dataset for the competitive intelligence use case.

The second dataset (`SEO_keyword_research` by sheryshisingh, 118 rows) contains keywords with search volume, CPC, and competition level. It's small and limited to email marketing, but it's sufficient for a demo. It replicates a SEMrush or Ahrefs export, which is something every SEO agency uses weekly.

The third dataset (`devra-ai-google-keyword-search-performance`, ~500 rows) contains keyword-level performance data with impressions, clicks, and average CPC. It's structured like a Google Ads export rather than a true Google Search Console export, but the columns map well enough to the use case.

The fourth set consists of three SERP topic files from eliasdabbas (5,360 combined rows), covering AI generators, language learning, and loans. These are used for the rank tracking use case. The raw files had 1,447 columns due to a nested JSON pagemap structure, which caused some parsing issues I had to work around. The fix was to select only the 8 columns I actually needed before concatenating the files.

All datasets are publicly available on Kaggle and don't contain any real client data, which keeps the project GDPR-compliant. For a production implementation, you'd replace these with live data pulled from SerpApi and Google Search Console.

The preprocessing is all handled by `data/explore_and_clean.py`. The main steps are filtering out paid results, standardizing column names, removing null rows, and computing a priority score for keywords (search volume × (1 - difficulty/100)). For the UC3 files, I also had to extract the date from the filename rather than parsing the queryTime column, which turned out to be a nested JSON object that exploded into hundreds of unusable columns.

---

## 3. Dashboard Design Rationale

The dashboard is built in Tableau and has three views, one per use case. I tried to design it around specific questions Chleo would ask in a client meeting, rather than just showing everything that was available in the data.

The first view answers "which domains dominate our target keywords?" using a frequency bar chart, and "which competitors rank highest on average?" using an average position bar chart. These two charts together give a quick competitive overview without requiring any SEO expertise to interpret.

The second view answers "which keywords should we prioritize for new content?" using a search volume bar chart. I also computed a priority score (volume × (1 - difficulty/100)) that gives a more balanced ranking than volume alone — a high-volume keyword that's very hard to rank for shouldn't automatically get more resources than a medium-volume keyword with low competition.

The third view shows rank tracking over time (using the demo data generated by `generate_demo_ranks.py`) with a color coding system where red means a significant drop and green means improvement. The goal is to give the account manager a "morning dashboard" they can glance at to know if anything needs urgent attention.

I used horizontal bar charts throughout because they're easy to read, support sorting intuitively, and work well with long domain or keyword names on the Y-axis. The color encoding follows the standard traffic light convention so it requires no explanation.

---

## 4. Agent Architecture

The agent is built with LangGraph and follows a sequential, deterministic flow rather than a ReAct-style loop. I chose this approach because the task is well-defined and multi-step — you always go through the same stages in the same order — so a state machine is cleaner and easier to debug than an open-ended reasoning loop.

The flow works like this: the agent receives a keyword and an optional client domain, then calls SerpApi to get the top-10 organic SERP results. It then scrapes each result URL using BeautifulSoup to extract the heading structure (H1, H2, H3) and a preview of the body text. These are then passed to Claude Haiku with an explicit instruction to identify content gaps "based ONLY on the provided text." Finally, the agent formats a report and saves it to a file.

The key design decision on the prompting side is the anti-hallucination constraint. By explicitly telling the LLM to base its analysis only on the text provided, I reduce the risk of it inventing gaps that aren't actually present in the competitor content. Every gap in the output should be traceable to at least one competitor heading.

For error handling, scraping failures fall back to the SERP snippet (title and meta description), which is always available from SerpApi. LLM errors are caught and logged to an error_log field in the agent state without stopping the pipeline. If JSON parsing fails, the raw LLM output is preserved rather than crashing.

The `tools.py` file adds two additional capabilities: keyword clustering (using OpenAI embeddings and K-Means) and rank drop detection (time-series analysis with a threshold of 3 positions). These cover use cases 2 and 3 respectively.

---

## 5. Evaluation Methodology

For evaluation I used two approaches in parallel: a custom LangSmith experiment with three automated evaluators, and a separate LLM-as-judge evaluation documented in `evaluation_report.md`.

The LangSmith experiment runs 15 pre-curated keyword examples through the agent and measures hallucination score (word overlap between gaps and competitor headings), gap coverage (overlap with manually-identified expected gaps), and format compliance (valid JSON with required keys). The results showed 100% format compliance and a hallucination score of 1.00, with an average cost of $0.001 per evaluation run.

The gap_coverage evaluator returned 0.00, but this reflects a weakness in the evaluator design rather than in the agent. The evaluator uses simple word matching, so if the agent uses "cost comparison" where the expected gap says "pricing table," it counts as a miss even though they mean the same thing. Manual review of the outputs showed the agent correctly identified the relevant gaps in 13 out of 15 examples. A semantic similarity-based evaluator using embeddings would give a more accurate score.

The LLM-as-judge evaluation is documented separately in `evaluation_report.md` and `evaluation_results.json`. The average overall score across 5 insights was 0.918, with actionability being the most variable criterion. The main limitation of this approach is that I used the same model (Claude Haiku) as both agent and judge, which introduces a self-evaluation bias. In a production setting I would use a different model family for the judge.