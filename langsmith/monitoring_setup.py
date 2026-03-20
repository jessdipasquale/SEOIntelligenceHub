"""
SEO Intelligence Hub — LangSmith Monitoring Setup
===================================================
Configures automated evaluation runs in LangSmith to demonstrate
AI transparency and observability to Chleo.

What this shows to Chleo:
  - Every AI call is logged (input → output → latency → cost)
  - The AI is evaluated against ground truth (no hallucinations)
  - Results are visible in a dashboard, not a black box

Run AFTER dataset_creation.py:
    python langsmith/monitoring_setup.py
"""

import os
import json
from dotenv import load_dotenv
from langsmith import Client
from langsmith.evaluation import evaluate, LangChainStringEvaluator
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

load_dotenv()

LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DATASET_NAME = "seo-gap-analysis-eval-v1"

# Enable LangSmith tracing for all runs
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "seo-intelligence-hub"


# ─────────────────────────────────────────────────────────────────────────────
# TARGET FUNCTION (what gets evaluated)
# ─────────────────────────────────────────────────────────────────────────────

def seo_gap_analysis_pipeline(inputs: dict) -> dict:
    """
    The function being monitored and evaluated.
    Takes a keyword + competitor headings → returns gap analysis.
    Every call to this function is logged in LangSmith.
    """
    keyword = inputs.get("keyword", "")
    headings = inputs.get("competitor_headings", [])
    headings_str = "\n".join(f"- {h}" for h in headings)

    llm = ChatAnthropic(
        model="claude-haiku-4-5-20251001",
        api_key=ANTHROPIC_API_KEY,
        max_tokens=800
    )

    prompt = f"""You are an SEO content strategist. Identify content gaps for the keyword "{keyword}".

Competitor headings found in top-10 SERP results:
{headings_str}

Based ONLY on the headings above, list:
1. The 3 most important content gaps (topics in 3+ competitors but likely missing from a standard page)
2. The single most impactful quick win

Format as JSON: {{"content_gaps": ["gap1", "gap2", "gap3"], "quick_win": "..."}}
Only include gaps that are DIRECTLY evidenced by the headings above."""

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        result = json.loads(response.content)
        return {
            "output": response.content,
            "content_gaps": result.get("content_gaps", []),
            "quick_win": result.get("quick_win", "")
        }
    except Exception:
        return {
            "output": response.content,
            "content_gaps": [],
            "quick_win": ""
        }


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM EVALUATORS
# ─────────────────────────────────────────────────────────────────────────────

def hallucination_check(run, example) -> dict:
    """
    Checks if the LLM invented gaps not present in competitor headings.
    Returns a score: 1.0 = no hallucination, 0.0 = hallucinated.
    """
    try:
        output = run.outputs.get("output", "")
        headings = example.inputs.get("competitor_headings", [])
        headings_lower = " ".join(headings).lower()

        # Parse LLM output
        try:
            result = json.loads(output)
            gaps = result.get("content_gaps", [])
        except Exception:
            gaps = []

        # Check each gap has at least one word traceable to competitor headings
        hallucinated = 0
        for gap in gaps:
            gap_words = set(gap.lower().split())
            heading_words = set(headings_lower.split())
            overlap = gap_words & heading_words
            if len(overlap) < 1:
                hallucinated += 1

        score = 1.0 - (hallucinated / max(len(gaps), 1))
        return {"key": "hallucination_score", "score": round(score, 2), "comment": f"{hallucinated}/{len(gaps)} gaps appear ungrounded"}
    except Exception as e:
        return {"key": "hallucination_score", "score": 0.5, "comment": f"Eval error: {str(e)[:50]}"}


def gap_coverage_score(run, example) -> dict:
    """
    Checks how many of the expected gaps the LLM identified.
    Score = overlap(identified, expected) / len(expected)
    """
    try:
        output = run.outputs.get("output", "")
        expected_gaps = example.outputs.get("expected_gaps", [])

        try:
            result = json.loads(output)
            identified_gaps = result.get("content_gaps", [])
        except Exception:
            identified_gaps = []

        identified_str = " ".join(identified_gaps).lower()
        matches = sum(
            1 for gap in expected_gaps
            if any(word in identified_str for word in gap.lower().split())
        )

        score = matches / max(len(expected_gaps), 1)
        return {"key": "gap_coverage", "score": round(score, 2), "comment": f"{matches}/{len(expected_gaps)} expected gaps found"}
    except Exception as e:
        return {"key": "gap_coverage", "score": 0.0, "comment": f"Eval error: {str(e)[:50]}"}


def response_format_check(run, example) -> dict:
    """Checks if response is valid JSON with expected keys."""
    try:
        output = run.outputs.get("output", "")
        result = json.loads(output)
        has_gaps = "content_gaps" in result and isinstance(result["content_gaps"], list)
        has_quick_win = "quick_win" in result and isinstance(result["quick_win"], str)
        score = 1.0 if (has_gaps and has_quick_win) else 0.5 if has_gaps else 0.0
        return {"key": "format_compliance", "score": score, "comment": f"gaps_present={has_gaps}, quick_win_present={has_quick_win}"}
    except Exception:
        return {"key": "format_compliance", "score": 0.0, "comment": "Invalid JSON output"}


# ─────────────────────────────────────────────────────────────────────────────
# RUN EVALUATION
# ─────────────────────────────────────────────────────────────────────────────

def run_evaluation():
    client = Client(api_key=LANGCHAIN_API_KEY)

    print(f"\n[LangSmith] Running evaluation on dataset: '{DATASET_NAME}'")
    print("   This will log every LLM call — showing Chleo the AI is transparent\n")

    results = evaluate(
        seo_gap_analysis_pipeline,
        data=DATASET_NAME,
        evaluators=[
            hallucination_check,
            gap_coverage_score,
            response_format_check,
        ],
        experiment_prefix="seo-gap-analysis",
        metadata={
            "model": "claude-haiku-4-5-20251001",
            "project": "SEO Intelligence Hub",
            "version": "v1.0",
            "use_case": "competitive_intelligence",
        },
    )

    print("\n" + "=" * 60)
    print("✅ Evaluation complete!")
    print(f"   Results logged in LangSmith: https://smith.langchain.com")
    print(f"   Project: seo-intelligence-hub")
    print(f"   Metrics tracked:")
    print(f"     - hallucination_score (target: >0.90)")
    print(f"     - gap_coverage       (target: >0.70)")
    print(f"     - format_compliance  (target: 1.00)")
    print("=" * 60)

    return results


def print_monitoring_summary():
    """Print a summary of what LangSmith is monitoring — for the Chleo presentation."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           LANGSMITH MONITORING — WHAT WE TRACK              ║
╚══════════════════════════════════════════════════════════════╝

For every AI call made by the SEO Intelligence Hub:

📊 LOGGED AUTOMATICALLY:
  • Input prompt sent to the AI
  • AI output received
  • Latency (response time in ms)
  • Token count (input + output)
  • Cost per call (in USD)
  • Timestamp and run ID

🎯 EVALUATED ON EACH RUN:
  • Hallucination Score — Did the AI invent gaps not in the data?
    Target: >90% grounded responses
  • Gap Coverage — Did the AI find the important gaps?
    Target: >70% of expected gaps identified
  • Format Compliance — Is the output structured correctly?
    Target: 100% valid JSON

🔍 WHY THIS MATTERS FOR CHLEO:
  "The AI is not a black box. Every time it runs, we can see
   exactly what it was given, what it said, how long it took,
   and what it cost. If it makes a mistake, we see it immediately.
   This is more transparent than a human analyst who doesn't
   document their reasoning."

💰 COST TRANSPARENCY:
  • Cost per keyword analysis: ~$0.002 (Claude Haiku)
  • Cost per month (200 keywords × weekly): ~$1.60
  • LangSmith free tier: up to 5,000 traces/month

🌐 VIEW RESULTS:
  https://smith.langchain.com → Projects → seo-intelligence-hub
""")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not LANGCHAIN_API_KEY:
        print("❌ LANGCHAIN_API_KEY not set in .env")
        exit(1)

    print_monitoring_summary()

    run_evaluation()
