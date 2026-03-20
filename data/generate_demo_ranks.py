"""
SEO Intelligence Hub — Generate Demo Rank Tracking Data
========================================================
Generates synthetic weekly rank tracking data for UC3 demo.
Run from project root:
    python data/generate_demo_ranks.py

Output:
    data/processed/rank_tracking_clean.csv  (overwrites existing)
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)
PROCESSED_DIR = "data/processed"

# Keywords per topic
keywords = {
    "ai_generators": [
        "ai content generator", "ai writing tool", "best ai writer",
        "chatgpt alternative", "ai copywriter", "free ai generator",
        "ai text generator", "ai blog writer", "jasper ai", "copy ai"
    ],
    "language_learning": [
        "learn spanish online", "best language app", "duolingo alternative",
        "learn french fast", "online language course", "language learning app",
        "learn japanese", "rosetta stone alternative", "babbel review", "learn mandarin"
    ],
    "loans": [
        "best personal loan", "low interest loan", "online loan application",
        "debt consolidation loan", "bad credit loan", "fast personal loan",
        "loan calculator", "compare loans", "instant loan approval", "loan refinancing"
    ]
}

# Domains per topic
domains = {
    "ai_generators": ["jasper.ai", "copy.ai", "writesonic.com", "rytr.me", "anyword.com",
                      "hypotenuse.ai", "peppertype.ai", "contentatscale.ai", "neuroflash.com", "simplified.com"],
    "language_learning": ["duolingo.com", "babbel.com", "rosettastone.com", "pimsleur.com", "busuu.com",
                          "italki.com", "lingoda.com", "languagetransfer.org", "clozemaster.com", "lingvist.com"],
    "loans": ["bankrate.com", "nerdwallet.com", "lendingtree.com", "sofi.com", "marcus.com",
              "lightstream.com", "discover.com", "prosper.com", "upstart.com", "lendingclub.com"]
}

# Generate weekly dates: 8 weeks
dates = pd.date_range(start="2023-01-01", periods=8, freq="W")

rows = []

for topic, kw_list in keywords.items():
    for keyword in kw_list:
        # Each keyword starts at a random position 1-10
        start_rank = np.random.randint(1, 11)
        current_rank = start_rank

        for i, date in enumerate(dates):
            # Simulate realistic rank movement
            # 70% chance of small change, 20% significant change, 10% big drop
            event = np.random.random()
            if event < 0.50:
                # Small improvement or stable
                change = np.random.randint(-2, 1)
            elif event < 0.75:
                # Gradual improvement
                change = np.random.randint(-3, -1)
            elif event < 0.90:
                # Small drop
                change = np.random.randint(1, 4)
            else:
                # Big drop (algorithm update / new competitor)
                change = np.random.randint(4, 8)

            current_rank = max(1, min(20, current_rank + change))

            # Pick a domain for this position
            domain = domains[topic][current_rank % len(domains[topic])]

            rows.append({
                "keyword": keyword,
                "rank": current_rank,
                "domain": domain,
                "date": date,
                "topic": topic,
                "country": "us"
            })

df = pd.DataFrame(rows)
df = df.sort_values(["keyword", "date"]).reset_index(drop=True)

# Compute rank change week over week
df["prev_rank"] = df.groupby("keyword")["rank"].shift(1)
df["rank_change"] = df["prev_rank"] - df["rank"]  # positive = improvement
df["rank_drop"] = df["rank_change"] < -3           # True = significant drop

os.makedirs(PROCESSED_DIR, exist_ok=True)
output_path = os.path.join(PROCESSED_DIR, "rank_tracking_clean.csv")
df.to_csv(output_path, index=False)

print("=" * 60)
print("Demo rank tracking data generated!")
print(f"   Rows  : {len(df):,}")
print(f"   Keywords: {df['keyword'].nunique()}")
print(f"   Weeks : {df['date'].nunique()}")
print(f"   Topics: {df['topic'].unique()}")
print(f"   Drops : {df['rank_drop'].sum()} significant drops detected")
print(f"   Saved : {output_path}")
print("=" * 60)