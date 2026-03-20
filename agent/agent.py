"""
SEO Intelligence Hub — Competitive Intelligence Agent
======================================================
LangGraph-based agent for automated SEO competitive analysis.

Use Case 1: Given a keyword, scrape top-10 SERP competitors,
extract content structure, run gap analysis, generate report.

Usage:
    python agent.py --keyword "best crm software" --client-domain "example.com"
"""

import os
import json
import argparse
import requests
from typing import TypedDict, Annotated, List, Optional
from datetime import datetime

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from bs4 import BeautifulSoup

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

SERP_API_KEY = os.getenv("SERP_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

# LangSmith tracing — set these to enable monitoring
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "seo-intelligence-hub"

# Use Claude Haiku for cost efficiency, upgrade to Sonnet for quality
LLM_MODEL = "claude-haiku-4-5-20251001"  # or "claude-sonnet-4-6", "gpt-4o-mini"


# ─────────────────────────────────────────────────────────────────────────────
# STATE DEFINITION
# ─────────────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    keyword: str
    client_domain: Optional[str]
    serp_results: List[dict]
    competitor_content: List[dict]
    gap_analysis: str
    final_report: str
    error_log: List[str]
    step: str


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — FETCH SERP RESULTS
# ─────────────────────────────────────────────────────────────────────────────

def fetch_serp_results(state: AgentState) -> AgentState:
    """Fetch top-10 SERP results for the target keyword via SerpApi."""
    keyword = state["keyword"]
    print(f"\n[STEP 1] Fetching SERP results for: '{keyword}'")

    try:
        params = {
            "engine": "google",
            "q": keyword,
            "num": 10,
            "api_key": SERP_API_KEY,
        }
        response = requests.get("https://serpapi.com/search", params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        organic_results = data.get("organic_results", [])
        serp_results = [
            {
                "position": r.get("position"),
                "title": r.get("title"),
                "url": r.get("link"),
                "domain": r.get("displayed_link", "").split("/")[0],
                "snippet": r.get("snippet", ""),
            }
            for r in organic_results[:10]
        ]

        print(f"   ✅ Retrieved {len(serp_results)} results")
        return {**state, "serp_results": serp_results, "step": "serp_done"}

    except Exception as e:
        error_msg = f"SERP fetch error: {str(e)}"
        print(f"   ❌ {error_msg}")
        return {**state, "error_log": state.get("error_log", []) + [error_msg], "step": "serp_failed"}


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — SCRAPE COMPETITOR CONTENT
# ─────────────────────────────────────────────────────────────────────────────

def scrape_competitor_content(state: AgentState) -> AgentState:
    """Extract heading structure and key content from each SERP result."""
    serp_results = state.get("serp_results", [])
    print(f"\n[STEP 2] Scraping {len(serp_results)} competitor pages...")

    competitor_content = []
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; SEOBot/1.0; +https://example.com/bot)"
    }

    for result in serp_results:
        url = result.get("url")
        if not url:
            continue

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Extract heading hierarchy
            headings = []
            for tag in ["h1", "h2", "h3"]:
                for el in soup.find_all(tag):
                    text = el.get_text(strip=True)
                    if text and len(text) > 3:
                        headings.append({"tag": tag.upper(), "text": text})

            # Extract first 500 words of body text
            paragraphs = soup.find_all("p")
            body_text = " ".join(p.get_text(strip=True) for p in paragraphs[:10])[:2000]

            competitor_content.append({
                "position": result["position"],
                "url": url,
                "domain": result.get("domain", ""),
                "headings": headings,
                "body_preview": body_text,
                "heading_count": len(headings),
                "scrape_success": True,
            })
            print(f"   ✅ Position {result['position']}: {result.get('domain')} ({len(headings)} headings)")

        except Exception as e:
            # Fallback: use snippet from SERP
            competitor_content.append({
                "position": result["position"],
                "url": url,
                "domain": result.get("domain", ""),
                "headings": [{"tag": "H1", "text": result.get("title", "")}],
                "body_preview": result.get("snippet", ""),
                "heading_count": 1,
                "scrape_success": False,
            })
            print(f"   ⚠️  Position {result['position']}: fallback to snippet ({str(e)[:50]})")

    print(f"   📊 Success rate: {sum(1 for c in competitor_content if c['scrape_success'])}/{len(competitor_content)}")
    return {**state, "competitor_content": competitor_content, "step": "scrape_done"}


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — LLM GAP ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def run_gap_analysis(state: AgentState) -> AgentState:
    """Use LLM to identify content gaps based on competitor structure."""
    print(f"\n[STEP 3] Running LLM gap analysis...")

    competitor_content = state.get("competitor_content", [])
    keyword = state["keyword"]
    client_domain = state.get("client_domain", "client's website")

    # Build context for LLM
    competitors_summary = []
    for comp in competitor_content[:10]:
        headings_str = "\n".join(f"  {h['tag']}: {h['text']}" for h in comp["headings"][:15])
        competitors_summary.append(
            f"Position {comp['position']} — {comp['domain']}:\n{headings_str}"
        )

    context = "\n\n---\n\n".join(competitors_summary)

    prompt = f"""You are an expert SEO content strategist. Analyze the top-10 SERP competitors for the keyword "{keyword}" and identify content gaps.

COMPETITOR CONTENT STRUCTURE (heading outlines from top-10 SERP results):
{context}

Based ONLY on the competitor content above (do not invent information), provide:

1. COMMON TOPICS (appear in 5+ competitors): Topics that are standard — the client must cover these.
2. CONTENT GAPS (appear in 3+ competitors but likely missing from a standard page): Topics that differentiate strong pages.
3. UNIQUE ANGLES (appear in 1-2 competitors): Differentiating content opportunities.
4. RECOMMENDED H2 STRUCTURE: A suggested heading outline for a new page targeting "{keyword}".
5. QUICK WIN: The single most important topic to add or improve immediately.

Format your response as structured JSON with keys: common_topics, content_gaps, unique_angles, recommended_structure, quick_win.
Keep all analysis grounded in the provided content — cite which competitor(s) cover each topic."""

    try:
        llm = ChatAnthropic(model=LLM_MODEL, api_key=ANTHROPIC_API_KEY, max_tokens=2000)
        response = llm.invoke([HumanMessage(content=prompt)])
        gap_analysis = response.content
        print(f"   ✅ Gap analysis completed ({len(gap_analysis)} chars)")
        return {**state, "gap_analysis": gap_analysis, "step": "analysis_done"}

    except Exception as e:
        error_msg = f"LLM gap analysis error: {str(e)}"
        print(f"   ❌ {error_msg}")
        return {**state, "error_log": state.get("error_log", []) + [error_msg], "step": "analysis_failed"}


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — GENERATE FINAL REPORT
# ─────────────────────────────────────────────────────────────────────────────

def generate_report(state: AgentState) -> AgentState:
    """Compile a human-readable report from the gap analysis."""
    print(f"\n[STEP 4] Generating final report...")

    keyword = state["keyword"]
    serp_results = state.get("serp_results", [])
    gap_analysis = state.get("gap_analysis", "")
    competitor_content = state.get("competitor_content", [])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Parse gap analysis JSON if possible
    try:
        analysis_data = json.loads(gap_analysis)
    except Exception:
        analysis_data = {"raw": gap_analysis}

    # Build competitor summary table
    comp_table = "\n".join(
        f"  {c['position']}. {c['domain']} — {c['heading_count']} headings {'✅' if c['scrape_success'] else '⚠️ fallback'}"
        for c in competitor_content
    )

    report = f"""
╔══════════════════════════════════════════════════════════════╗
║         SEO COMPETITIVE INTELLIGENCE REPORT                  ║
╚══════════════════════════════════════════════════════════════╝

Keyword:     {keyword}
Generated:   {timestamp}
Pages scraped: {len(competitor_content)} / 10

─── TOP-10 COMPETITOR OVERVIEW ────────────────────────────────
{comp_table}

─── GAP ANALYSIS ───────────────────────────────────────────────
{json.dumps(analysis_data, indent=2, ensure_ascii=False) if isinstance(analysis_data, dict) else gap_analysis}

─── ERRORS / FALLBACKS ─────────────────────────────────────────
{chr(10).join(state.get("error_log", ["None"])) or "None"}

════════════════════════════════════════════════════════════════
Report generated by SEO Intelligence Hub | Monitored via LangSmith
"""

    # Save report to file
    report_path = f"reports/gap_analysis_{keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    os.makedirs("reports", exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"   ✅ Report saved: {report_path}")
    return {**state, "final_report": report, "step": "done"}


# ─────────────────────────────────────────────────────────────────────────────
# GRAPH DEFINITION
# ─────────────────────────────────────────────────────────────────────────────

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("fetch_serp", fetch_serp_results)
    graph.add_node("scrape_content", scrape_competitor_content)
    graph.add_node("gap_analysis", run_gap_analysis)
    graph.add_node("generate_report", generate_report)

    graph.set_entry_point("fetch_serp")
    graph.add_edge("fetch_serp", "scrape_content")
    graph.add_edge("scrape_content", "gap_analysis")
    graph.add_edge("gap_analysis", "generate_report")
    graph.add_edge("generate_report", END)

    return graph.compile()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SEO Competitive Intelligence Agent")
    parser.add_argument("--keyword", required=True, help="Target keyword to analyze")
    parser.add_argument("--client-domain", default=None, help="Client domain (for context)")
    args = parser.parse_args()

    app = build_graph()

    initial_state: AgentState = {
        "keyword": args.keyword,
        "client_domain": args.client_domain,
        "serp_results": [],
        "competitor_content": [],
        "gap_analysis": "",
        "final_report": "",
        "error_log": [],
        "step": "start",
    }

    print(f"\n🚀 Starting SEO Intelligence Agent")
    print(f"   Keyword: {args.keyword}")
    print(f"   LangSmith project: seo-intelligence-hub")

    result = app.invoke(initial_state)

    print("\n" + "=" * 60)
    print("✅ Analysis complete!")
    print(result["final_report"])
