"""
SEO Intelligence Hub — LangSmith Dataset Creation
===================================================
Creates a small evaluation dataset in LangSmith to demonstrate
AI monitoring and transparency to Chleo.

The dataset contains:
- 15 keyword gap analysis examples
- Each example: input (keyword + competitor content) → expected output (gap analysis)
- Used to evaluate hallucination rate and analysis quality

Setup:
    1. Create account at https://smith.langchain.com
    2. Get API key from Settings → API Keys
    3. Add to .env: LANGCHAIN_API_KEY=ls_...
    4. Run: python langsmith/dataset_creation.py
"""

import os
import json
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
DATASET_NAME = "seo-gap-analysis-eval-v1"

# ─────────────────────────────────────────────────────────────────────────────
# EVALUATION DATASET — 15 examples with ground truth
# ─────────────────────────────────────────────────────────────────────────────
# These are manually verified examples:
# Input = keyword + simulated competitor headings
# Output = what a good SEO analyst would identify as the main gap

EVAL_EXAMPLES = [
    {
        "input": {
            "keyword": "best project management software",
            "competitor_headings": [
                "What is project management software?",
                "Key features to look for",
                "Top 10 project management tools compared",
                "Pricing comparison",
                "Best for small teams",
                "Best for enterprise",
                "Free vs paid options",
                "How to choose the right tool",
                "Integration with other tools",
                "Customer reviews and ratings"
            ]
        },
        "expected_gaps": ["pricing comparison", "free vs paid options", "integration capabilities"],
        "expected_quick_win": "Add a pricing comparison table",
        "difficulty": "easy"
    },
    {
        "input": {
            "keyword": "how to do keyword research",
            "competitor_headings": [
                "What is keyword research?",
                "Why keyword research matters",
                "Step-by-step keyword research process",
                "Best keyword research tools",
                "Long-tail vs short-tail keywords",
                "Search intent explained",
                "Keyword difficulty explained",
                "How to find low competition keywords",
                "Keyword research for SEO beginners",
                "Free keyword research tools"
            ]
        },
        "expected_gaps": ["search intent", "keyword difficulty", "long-tail vs short-tail distinction"],
        "expected_quick_win": "Add section on search intent classification",
        "difficulty": "easy"
    },
    {
        "input": {
            "keyword": "best CRM for small business",
            "competitor_headings": [
                "Top CRM software for small businesses",
                "What features does a small business CRM need?",
                "HubSpot vs Salesforce vs Zoho comparison",
                "Free CRM options",
                "How much does CRM software cost?",
                "CRM setup guide",
                "Integrations with email and Slack",
                "Mobile CRM apps",
                "Customer support comparison",
                "Which CRM is right for your industry?"
            ]
        },
        "expected_gaps": ["industry-specific CRM recommendations", "mobile app availability", "customer support quality"],
        "expected_quick_win": "Add industry-specific CRM recommendations section",
        "difficulty": "medium"
    },
    {
        "input": {
            "keyword": "content marketing strategy",
            "competitor_headings": [
                "What is content marketing?",
                "Content marketing vs traditional marketing",
                "How to build a content marketing strategy",
                "Content calendar template",
                "Types of content that drive traffic",
                "How to measure content marketing ROI",
                "B2B vs B2C content marketing",
                "Content distribution channels",
                "Content repurposing strategies",
                "AI tools for content marketing"
            ]
        },
        "expected_gaps": ["content calendar template", "ROI measurement", "AI tools for content"],
        "expected_quick_win": "Add content calendar template as downloadable resource",
        "difficulty": "medium"
    },
    {
        "input": {
            "keyword": "technical SEO audit",
            "competitor_headings": [
                "What is a technical SEO audit?",
                "Technical SEO audit checklist",
                "Crawlability and indexation issues",
                "Site speed optimization",
                "Core Web Vitals explained",
                "Structured data and schema markup",
                "Mobile-first indexing",
                "Duplicate content issues",
                "Internal linking structure",
                "How to fix technical SEO issues"
            ]
        },
        "expected_gaps": ["Core Web Vitals", "structured data/schema markup", "mobile-first indexing"],
        "expected_quick_win": "Add Core Web Vitals section with specific metrics",
        "difficulty": "hard"
    },
    {
        "input": {
            "keyword": "email marketing best practices",
            "competitor_headings": [
                "Email marketing statistics 2024",
                "How to build an email list",
                "Email subject line best practices",
                "Segmentation strategies",
                "A/B testing for email",
                "Email automation workflows",
                "Avoiding spam filters",
                "Email design tips",
                "Measuring email campaign performance",
                "GDPR compliance for email marketing"
            ]
        },
        "expected_gaps": ["GDPR compliance", "email automation workflows", "spam filter avoidance"],
        "expected_quick_win": "Add GDPR compliance section",
        "difficulty": "medium"
    },
    {
        "input": {
            "keyword": "link building strategies",
            "competitor_headings": [
                "What is link building?",
                "White hat vs black hat link building",
                "Guest posting guide",
                "Broken link building",
                "HARO for link building",
                "Digital PR strategies",
                "Skyscraper technique",
                "How to get .edu and .gov links",
                "Link building outreach templates",
                "Measuring link building success"
            ]
        },
        "expected_gaps": ["digital PR strategies", "HARO", "outreach templates"],
        "expected_quick_win": "Add outreach email templates section",
        "difficulty": "hard"
    },
    {
        "input": {
            "keyword": "social media marketing tools",
            "competitor_headings": [
                "Best social media management tools",
                "Buffer vs Hootsuite vs Sprout Social",
                "Free social media tools",
                "Tools for scheduling posts",
                "Analytics tools for social media",
                "Design tools for social media",
                "Influencer marketing platforms",
                "Social listening tools",
                "AI tools for social media",
                "Pricing comparison"
            ]
        },
        "expected_gaps": ["social listening tools", "influencer marketing platforms", "AI tools"],
        "expected_quick_win": "Add AI tools for social media section",
        "difficulty": "easy"
    },
    {
        "input": {
            "keyword": "ecommerce SEO guide",
            "competitor_headings": [
                "What is ecommerce SEO?",
                "Product page optimization",
                "Category page SEO",
                "Technical SEO for ecommerce",
                "Keyword research for ecommerce",
                "Schema markup for products",
                "User-generated content for SEO",
                "International ecommerce SEO",
                "Site structure best practices",
                "Common ecommerce SEO mistakes"
            ]
        },
        "expected_gaps": ["schema markup for products", "user-generated content", "international SEO"],
        "expected_quick_win": "Add product schema markup implementation guide",
        "difficulty": "hard"
    },
    {
        "input": {
            "keyword": "google analytics 4 tutorial",
            "competitor_headings": [
                "What is Google Analytics 4?",
                "GA4 vs Universal Analytics",
                "How to set up GA4",
                "Understanding GA4 reports",
                "Custom events in GA4",
                "GA4 audience building",
                "Connecting GA4 to Google Ads",
                "GA4 attribution models",
                "Common GA4 mistakes",
                "GA4 for ecommerce tracking"
            ]
        },
        "expected_gaps": ["GA4 vs Universal Analytics comparison", "attribution models", "ecommerce tracking"],
        "expected_quick_win": "Add GA4 vs Universal Analytics migration section",
        "difficulty": "medium"
    },
    {
        "input": {
            "keyword": "local SEO tips",
            "competitor_headings": [
                "What is local SEO?",
                "Google Business Profile optimization",
                "Local keyword research",
                "Building local citations",
                "Getting more Google reviews",
                "Local link building",
                "NAP consistency",
                "Local schema markup",
                "Tracking local rankings",
                "Local SEO for multiple locations"
            ]
        },
        "expected_gaps": ["NAP consistency", "local schema markup", "multiple locations"],
        "expected_quick_win": "Add Google Business Profile optimization checklist",
        "difficulty": "easy"
    },
    {
        "input": {
            "keyword": "seo reporting template",
            "competitor_headings": [
                "What to include in an SEO report",
                "Monthly SEO report template",
                "KPIs to track in SEO",
                "How to present SEO results to clients",
                "Automated SEO reporting tools",
                "SEO dashboard examples",
                "White-label SEO reports",
                "Frequency of SEO reports",
                "Common SEO report mistakes",
                "Free SEO report templates"
            ]
        },
        "expected_gaps": ["white-label reports", "automated reporting tools", "dashboard examples"],
        "expected_quick_win": "Add downloadable SEO report template",
        "difficulty": "easy"
    },
    {
        "input": {
            "keyword": "on page seo checklist",
            "competitor_headings": [
                "What is on-page SEO?",
                "Title tag optimization",
                "Meta description best practices",
                "Header tag structure",
                "Image optimization",
                "Internal linking strategy",
                "URL structure",
                "Page speed for on-page SEO",
                "Content optimization tips",
                "On-page SEO tools"
            ]
        },
        "expected_gaps": ["URL structure optimization", "page speed impact", "on-page SEO tools"],
        "expected_quick_win": "Add interactive on-page SEO checklist",
        "difficulty": "easy"
    },
    {
        "input": {
            "keyword": "voice search optimization",
            "competitor_headings": [
                "What is voice search SEO?",
                "How voice search differs from text search",
                "Featured snippets and voice search",
                "Optimizing for conversational queries",
                "Local voice search optimization",
                "Structured data for voice search",
                "Voice search statistics 2024",
                "How to do voice search keyword research",
                "Voice search and mobile SEO",
                "Future of voice search"
            ]
        },
        "expected_gaps": ["featured snippets connection", "structured data for voice", "conversational query optimization"],
        "expected_quick_win": "Add FAQ section targeting conversational queries",
        "difficulty": "hard"
    },
    {
        "input": {
            "keyword": "seo audit tool",
            "competitor_headings": [
                "Best SEO audit tools 2024",
                "Free vs paid SEO audit tools",
                "Screaming Frog vs Sitebulb comparison",
                "How to run a site audit",
                "Technical SEO audit checklist",
                "SEO audit for beginners",
                "Automated vs manual SEO audits",
                "How often to audit your site",
                "What to do after an SEO audit",
                "SEO audit pricing"
            ]
        },
        "expected_gaps": ["tool comparison (Screaming Frog vs Sitebulb)", "audit frequency recommendations", "post-audit action plan"],
        "expected_quick_win": "Add tool comparison table",
        "difficulty": "medium"
    }
]


# ─────────────────────────────────────────────────────────────────────────────
# CREATE LANGSMITH DATASET
# ─────────────────────────────────────────────────────────────────────────────

def create_evaluation_dataset():
    client = Client(api_key=LANGCHAIN_API_KEY)

    print(f"\n[LangSmith] Creating evaluation dataset: '{DATASET_NAME}'")

    # Create dataset
    try:
        dataset = client.create_dataset(
            dataset_name=DATASET_NAME,
            description="SEO gap analysis evaluation dataset. Tests whether the LLM correctly identifies content gaps based on SERP competitor headings, without hallucinating topics not present in the input.",
        )
        print(f"   ✅ Dataset created: {dataset.id}")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"   ℹ️  Dataset already exists, fetching...")
            datasets = list(client.list_datasets(dataset_name=DATASET_NAME))
            dataset = datasets[0]
        else:
            raise e

    # Add examples to dataset
    print(f"   Adding {len(EVAL_EXAMPLES)} evaluation examples...")

    examples_created = 0
    for i, example in enumerate(EVAL_EXAMPLES):
        try:
            client.create_example(
                inputs={
                    "keyword": example["input"]["keyword"],
                    "competitor_headings": example["input"]["competitor_headings"],
                    "prompt": f"Analyze content gaps for keyword: '{example['input']['keyword']}'. Competitor headings: {json.dumps(example['input']['competitor_headings'])}"
                },
                outputs={
                    "expected_gaps": example["expected_gaps"],
                    "expected_quick_win": example["expected_quick_win"],
                },
                metadata={
                    "difficulty": example["difficulty"],
                    "example_id": i + 1,
                },
                dataset_id=dataset.id,
            )
            examples_created += 1
            print(f"   ✅ Example {i+1}/15: '{example['input']['keyword']}' ({example['difficulty']})")
        except Exception as e:
            print(f"   ❌ Example {i+1} failed: {str(e)[:50]}")

    print(f"\n   Dataset ready: {examples_created}/{len(EVAL_EXAMPLES)} examples created")
    print(f"   View at: https://smith.langchain.com → Datasets → {DATASET_NAME}")

    return dataset


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not LANGCHAIN_API_KEY:
        print("❌ LANGCHAIN_API_KEY not set in .env file")
        print("   Get your key at: https://smith.langchain.com → Settings → API Keys")
        exit(1)

    create_evaluation_dataset()

    print("\n" + "=" * 60)
    print("✅ LangSmith dataset ready!")
    print("   Next step: run monitoring_setup.py to configure evaluators")
    print("=" * 60)
