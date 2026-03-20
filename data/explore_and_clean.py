"""
SEO Intelligence Hub — Data Exploration & Cleaning
===================================================
Run this script from the project root folder:
    python data/explore_and_clean.py
"""

import pandas as pd
import numpy as np
import os
import warnings

warnings.filterwarnings("ignore")

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)


def save_clean(df, filename, label):
    path = os.path.join(PROCESSED_DIR, filename)
    df.to_csv(path, index=False)
    print(f"\n  Saved: {label}")
    print(f"   Path : {path}")
    print(f"   Shape: {df.shape[0]:,} rows x {df.shape[1]} cols")
    print(f"   Cols : {list(df.columns)}")
    print(f"   Sample:\n{df.head(2).to_string()}")


def clean_serp_data():
    path = os.path.join(RAW_DIR, "GoogleRankProductDaily_2022-04-21_USECASE1.csv")
    print(f"\n{'='*60}\nLoading UC1 - SERP data\n   {path}")
    df = pd.read_csv(path, low_memory=False)
    print(f"   Raw shape: {df.shape}")
    if "is_ad" in df.columns:
        df = df[df["is_ad"] == 0]
    df = df.rename(columns={
        "keywordname": "query",
        "position":    "position",
        "url":         "url",
        "domain":      "domain",
        "title":       "title",
        "scandate":    "date",
    })
    keep = [c for c in ["query", "position", "url", "domain", "title", "date", "city"] if c in df.columns]
    df = df[keep].copy()
    df["position"] = pd.to_numeric(df["position"], errors="coerce")
    df = df[df["position"].between(1, 100)]
    df["position"] = df["position"].astype(int)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["is_top_10"] = df["position"] <= 10
    df.drop_duplicates(inplace=True)
    df.dropna(subset=["query", "position"], inplace=True)
    save_clean(df, "serp_clean.csv", "UC1 - SERP Clean")
    return df


def clean_keyword_research():
    path = os.path.join(RAW_DIR, "SEO_keyword_research_USECASE2_USECASE2.csv")
    print(f"\n{'='*60}\nLoading UC2a - Keyword Research\n   {path}")
    df = pd.read_csv(path, low_memory=False)
    print(f"   Raw shape: {df.shape}")
    df = df.rename(columns={
        "text":        "keyword",
        "vol":         "search_volume",
        "cpc":         "cpc",
        "competition": "competition",
        "score":       "score",
    })
    df = df[[c for c in df.columns if not c.startswith("Unnamed")]]
    df.dropna(subset=["keyword"], inplace=True)
    df = df[df["keyword"].astype(str).str.strip() != ""]
    for col in ["search_volume", "cpc", "score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "search_volume" in df.columns:
        df = df[df["search_volume"] > 0]
    if "competition" in df.columns:
        comp_map = {"low": 25, "medium": 55, "high": 80}
        df["difficulty"] = df["competition"].astype(str).str.lower().map(comp_map).fillna(50)
    else:
        df["difficulty"] = 50
    if "search_volume" in df.columns:
        df["priority_score"] = (df["search_volume"] * (1 - df["difficulty"] / 100)).round(2)
        df = df.nlargest(5000, "search_volume")
    save_clean(df, "keywords_clean.csv", "UC2a - Keywords Clean")
    return df


def clean_gsc_performance():
    path = os.path.join(RAW_DIR, "devra-ai-google-keyword-search-performance_USECASE2.csv")
    print(f"\n{'='*60}\nLoading UC2b - Keyword Performance\n   {path}")
    df = pd.read_csv(path, low_memory=False)
    print(f"   Raw shape: {df.shape}")
    df = df.rename(columns={
        "Search term": "query",
        "Keyword":     "keyword_group",
        "Impr.":       "impressions",
        "Clicks":      "clicks",
        "Avg. CPC":    "avg_cpc",
        "Match type":  "match_type",
    })
    df.dropna(subset=["query"], inplace=True)
    for col in ["impressions", "clicks"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    if "avg_cpc" in df.columns:
        df["avg_cpc"] = pd.to_numeric(df["avg_cpc"], errors="coerce")
    if "clicks" in df.columns and "impressions" in df.columns:
        df["ctr"] = (df["clicks"] / df["impressions"].replace(0, np.nan)).round(4)
    if "ctr" in df.columns and "impressions" in df.columns:
        df["opportunity_clicks"] = (df["impressions"] * (1 - df["ctr"].fillna(0))).round(0).astype(int)
    save_clean(df, "gsc_performance_clean.csv", "UC2b - GSC Performance Clean")
    return df


def clean_rank_tracking():
    # Select only needed columns PER FILE before concat
    # to avoid 1447-column explosion and duplicate column issues
    files = {
        "ai_generators":     ("serp_language_ai_generators_2023_01_28_USECASE3.csv", "2023-01-28"),
        "language_learning": ("serp_language_learning_2023_01_25_USECASE3.csv",      "2023-01-25"),
        "loans":             ("serp_loans_2023_02_14_USECASE3.csv",                  "2023-02-14"),
    }

    # Original column names we want from each file
    original_cols = {
        "searchTerms": "keyword",
        "rank":        "rank",
        "title":       "title",
        "snippet":     "snippet",
        "displayLink": "domain",
        "link":        "url",
        "gl":          "country",
    }

    dfs = []
    for topic, (filename, file_date) in files.items():
        path = os.path.join(RAW_DIR, filename)
        print(f"\n{'='*60}\nLoading UC3 - {topic}\n   {path}")
        df = pd.read_csv(path, low_memory=False)
        print(f"   Raw shape: {df.shape}")

        # Select only the original columns that exist, then rename
        cols_to_keep = {orig: new for orig, new in original_cols.items() if orig in df.columns}
        df = df[list(cols_to_keep.keys())].copy()
        df = df.rename(columns=cols_to_keep)

        df["topic"] = topic
        df["date"] = pd.Timestamp(file_date)
        print(f"   Trimmed shape: {df.shape}")
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    print(f"\n   Combined shape: {combined.shape}")

    combined["rank"] = pd.to_numeric(combined["rank"], errors="coerce")
    combined = combined[combined["rank"].between(1, 100)]
    combined["rank"] = combined["rank"].astype(int)
    combined.drop_duplicates(inplace=True)
    combined.dropna(subset=["keyword", "rank"], inplace=True)

    combined = combined.sort_values(["keyword", "date"]).reset_index(drop=True)
    combined["prev_rank"] = combined.groupby("keyword")["rank"].shift(1)
    combined["rank_change"] = combined["prev_rank"] - combined["rank"]
    combined["rank_drop"] = combined["rank_change"] < -3

    save_clean(combined, "rank_tracking_clean.csv", "UC3 - Rank Tracking Clean")
    return combined


if __name__ == "__main__":
    print("=" * 60)
    print("SEO Intelligence Hub - Data Cleaning")
    print("=" * 60)
    serp_df = clean_serp_data()
    kw_df   = clean_keyword_research()
    gsc_df  = clean_gsc_performance()
    rank_df = clean_rank_tracking()
    print("\n" + "=" * 60)
    print("All datasets cleaned and saved to data/processed/")
    print("Next step: open Tableau and connect to the processed CSVs")
    print("=" * 60)