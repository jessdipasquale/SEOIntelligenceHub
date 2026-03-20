"""
SEO Intelligence Hub — Agent Tools
====================================
Standalone tools for keyword clustering and rank drop detection.
These can be imported by agent.py or run independently.
"""

import os
import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


# ─────────────────────────────────────────────────────────────────────────────
# TOOL: KEYWORD CLUSTERING (Use Case 2)
# ─────────────────────────────────────────────────────────────────────────────

def cluster_keywords(keywords_csv: str, n_clusters: int = 10, output_csv: str = "data/processed/keywords_clustered.csv") -> pd.DataFrame:
    """
    Cluster keywords semantically using embeddings + K-Means.
    Classifies each cluster's dominant search intent via LLM.

    Args:
        keywords_csv: path to keywords_clean.csv
        n_clusters: number of topic clusters (default 10)
        output_csv: where to save the clustered output

    Returns:
        DataFrame with columns: keyword, cluster_id, cluster_label, intent, priority_score
    """
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import normalize
    from openai import OpenAI
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import HumanMessage

    print(f"\n[TOOL] Keyword Clustering")
    print(f"   Input: {keywords_csv}")

    df = pd.read_csv(keywords_csv)
    keywords = df["keyword"].dropna().tolist()
    print(f"   Keywords to cluster: {len(keywords)}")

    # Step 1: Generate embeddings
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("   Generating embeddings (text-embedding-3-small)...")

    # Batch embeddings to stay within API limits
    batch_size = 100
    all_embeddings = []
    for i in range(0, len(keywords), batch_size):
        batch = keywords[i:i + batch_size]
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=batch
        )
        batch_embeddings = [e.embedding for e in response.data]
        all_embeddings.extend(batch_embeddings)
        print(f"   Embedded {min(i + batch_size, len(keywords))}/{len(keywords)}")

    embeddings_matrix = np.array(all_embeddings)
    embeddings_normalized = normalize(embeddings_matrix)

    # Step 2: K-Means clustering
    print(f"   Clustering into {n_clusters} groups...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_ids = kmeans.fit_predict(embeddings_normalized)
    df["cluster_id"] = cluster_ids

    # Step 3: Label each cluster with LLM
    print("   Labeling clusters with LLM...")
    llm = ChatAnthropic(model="claude-haiku-4-5-20251001", api_key=ANTHROPIC_API_KEY, max_tokens=500)
    cluster_labels = {}
    cluster_intents = {}

    for cluster_id in range(n_clusters):
        cluster_kws = df[df["cluster_id"] == cluster_id]["keyword"].tolist()[:20]
        sample = ", ".join(cluster_kws[:15])

        prompt = f"""Given these keywords from a keyword research dataset, provide:
1. A SHORT topic label (3-5 words max) that describes the semantic theme
2. The dominant search intent: informational / navigational / transactional / commercial

Keywords: {sample}

Respond in JSON format: {{"label": "...", "intent": "..."}}"""

        response = llm.invoke([HumanMessage(content=prompt)])
        try:
            import json
            result = json.loads(response.content)
            cluster_labels[cluster_id] = result.get("label", f"Cluster {cluster_id}")
            cluster_intents[cluster_id] = result.get("intent", "informational")
        except Exception:
            cluster_labels[cluster_id] = f"Cluster {cluster_id}"
            cluster_intents[cluster_id] = "informational"

        print(f"   Cluster {cluster_id}: {cluster_labels[cluster_id]} ({cluster_intents[cluster_id]})")

    df["cluster_label"] = df["cluster_id"].map(cluster_labels)
    df["intent"] = df["cluster_id"].map(cluster_intents)

    # Step 4: Compute priority score
    if "search_volume" in df.columns and "difficulty" in df.columns:
        df["priority_score"] = (df["search_volume"] * (1 - df["difficulty"] / 100)).round(2)

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"   ✅ Clustered keywords saved: {output_csv}")

    return df


# ─────────────────────────────────────────────────────────────────────────────
# TOOL: RANK DROP DETECTION (Use Case 3)
# ─────────────────────────────────────────────────────────────────────────────

def detect_rank_drops(
    rank_csv: str,
    drop_threshold: int = 3,
    output_csv: str = "data/processed/rank_alerts.csv"
) -> pd.DataFrame:
    """
    Detect significant keyword rank drops from tracking data.
    Generates a contextual root cause hypothesis via LLM for each drop.

    Args:
        rank_csv: path to rank_tracking_clean.csv
        drop_threshold: minimum rank position change to flag (default: 3)
        output_csv: where to save alert output

    Returns:
        DataFrame with flagged drops and root cause hypotheses
    """
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import HumanMessage

    print(f"\n[TOOL] Rank Drop Detection")
    print(f"   Input: {rank_csv}")
    print(f"   Drop threshold: >{drop_threshold} positions")

    df = pd.read_csv(rank_csv, parse_dates=["date"] if "date" in pd.read_csv(rank_csv, nrows=1).columns else None)

    # Detect keyword and date columns
    kw_col = next((c for c in df.columns if "keyword" in c or "query" in c), df.columns[0])
    rank_col = "rank" if "rank" in df.columns else next((c for c in df.columns if "position" in c), None)

    if rank_col is None:
        raise ValueError("Could not find rank/position column in dataset")

    # Sort and compute week-over-week change
    if "date" in df.columns:
        df = df.sort_values([kw_col, "date"])
        df["prev_rank"] = df.groupby(kw_col)[rank_col].shift(1)
    else:
        df["prev_rank"] = df.groupby(kw_col)[rank_col].shift(1)

    df["rank_change"] = df["prev_rank"] - df[rank_col]
    df["is_drop"] = df["rank_change"] < -drop_threshold

    drops = df[df["is_drop"]].copy()
    print(f"   Drops detected: {len(drops)}")

    if drops.empty:
        print("   ✅ No significant rank drops detected!")
        return drops

    # Generate LLM root cause hypothesis for top drops
    llm = ChatAnthropic(model="claude-haiku-4-5-20251001", api_key=ANTHROPIC_API_KEY, max_tokens=300)
    hypotheses = []

    for _, row in drops.iterrows():
        kw = row[kw_col]
        prev = row["prev_rank"]
        curr = row[rank_col]
        change = abs(row["rank_change"])

        prompt = f"""An SEO keyword just dropped {change:.0f} positions (from #{prev:.0f} to #{curr:.0f}).
Keyword: "{kw}"

Provide a brief root cause hypothesis (2-3 sentences max) with:
1. Most likely cause
2. One recommended action

Keep it practical for an SEO account manager."""

        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            hypothesis = response.content.strip()
        except Exception as e:
            hypothesis = f"Analysis unavailable: {str(e)[:50]}"

        hypotheses.append(hypothesis)
        severity = "🔴 CRITICAL" if change > 10 else "🟡 WARNING" if change > 5 else "⚪ MINOR"
        print(f"   {severity} | {kw}: -{change:.0f} positions → {hypothesis[:80]}...")

    drops["root_cause_hypothesis"] = hypotheses
    drops["severity"] = drops["rank_change"].abs().apply(
        lambda x: "critical" if x > 10 else "warning" if x > 5 else "minor"
    )

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    drops.to_csv(output_csv, index=False)
    print(f"\n   ✅ Alerts saved: {output_csv}")

    return drops


# ─────────────────────────────────────────────────────────────────────────────
# QUICK STATS TOOL
# ─────────────────────────────────────────────────────────────────────────────

def compute_serp_stats(serp_csv: str) -> Dict:
    """Compute basic statistics from SERP data for dashboard."""
    df = pd.read_csv(serp_csv)

    stats = {
        "total_keywords": df["query"].nunique() if "query" in df.columns else 0,
        "total_domains": df["domain"].nunique() if "domain" in df.columns else 0,
        "top_domains": df["domain"].value_counts().head(10).to_dict() if "domain" in df.columns else {},
        "avg_position_by_domain": df.groupby("domain")["position"].mean().round(1).to_dict() if "domain" in df.columns else {},
    }

    print("\n[TOOL] SERP Statistics")
    print(f"   Total keywords: {stats['total_keywords']}")
    print(f"   Unique domains: {stats['total_domains']}")
    print(f"   Top domains: {list(stats['top_domains'].keys())[:5]}")

    return stats


if __name__ == "__main__":
    # Quick test
    print("Tools module loaded. Import and call functions directly.")
    print("Available tools:")
    print("  - cluster_keywords(keywords_csv, n_clusters)")
    print("  - detect_rank_drops(rank_csv, drop_threshold)")
    print("  - compute_serp_stats(serp_csv)")
