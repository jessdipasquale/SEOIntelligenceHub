# Implementation Timeline — SEO Intelligence Hub

**Client:** Chleo's Digital SEO Agency

---

## Phase Overview

| Phase | Duration | Goal |
|---|---|---|
| Phase 0 — Pilot Setup | Week 1–2 | Infrastructure up, first keyword analyzed |
| Phase 1 — Core MVP | Week 3–6 | UC1 live for 5 clients |
| Phase 2 — Expansion | Week 7–10 | UC2 + UC3 live, full client rollout |
| Phase 3 — Optimization | Week 11–12 | Fine-tuning, training, handover |

---

## Detailed Timeline

### Phase 0 — Pilot Setup (Week 1–2)

**Week 1**
- Day 1–2: Environment setup (Python, API keys, n8n cloud, LangSmith account, Pinecone)
- Day 3–4: Test SerpApi with 5 keywords manually, validate scraping success rate
- Day 5: Deploy agent.py, run first end-to-end test

**Week 2**
- Day 1–2: Import n8n workflow, configure scheduler + email
- Day 3: LangSmith monitoring active, first evaluation run
- Day 4–5: QA with 10 real keywords across 2 clients

**Milestone:** First automated report delivered to a real client ✅

---

### Phase 1 — Core MVP (Week 3–6): Use Case 1

**Week 3**
- Define keyword watchlist for 5 pilot clients (25 keywords each)
- Finalize email report template with client branding
- Set up Tableau dashboard with real SERP data

**Week 4**
- First real 3-day automated cycle runs
- Review LangSmith logs with team — demonstrate transparency
- Collect feedback from pilot clients on report format

**Week 5**
- Address feedback: adjust prompt, refine report structure
- Expand to 10 clients
- Team training: 1 session (2h) — how to use the system

**Week 6**
- Full QA: verify scraping success rate >70%, no missed email sends
- Cost review: actual vs estimated API costs

**Milestone:** Use Case 1 running for 10 clients, 250 keywords monitored ✅

---

### Phase 2 — Expansion (Week 7–10): Use Cases 2 & 3

**Week 7**
- Deploy tools.py: keyword clustering pipeline
- Run first batch clustering on one client's keyword export
- Validate intent classification accuracy manually (sample of 50 keywords)

**Week 8**
- Deploy rank drop detection (tools.py → detect_rank_drops)
- Configure Slack alert in n8n for drop notifications
- Test with historical rank data from SERP dataset

**Week 9**
- Integrate Tableau dashboard with clustering + rank data
- Full client rollout: all 28 clients, all 3 use cases
- Second team training session (2h): reading AI reports, acting on alerts

**Week 10**
- Monitor system for 2 weeks at full scale
- Review LangSmith metrics: hallucination score, coverage score
- Adjust any prompts based on real-world performance

**Milestone:** All 3 use cases live for all clients ✅

---

### Phase 3 — Optimization & Handover (Week 11–12)

**Week 11**
- Performance review meeting with Chleo
- Present ROI: hours saved, labor cost reduction, client feedback
- Document any issues and resolutions

**Week 12**
- Final LangSmith monitoring report (4-week performance summary)
- Handover documentation: how to update keywords, adjust prompts, monitor costs
- Define v2 roadmap: content brief generation, backlink alerts, multi-language

**Milestone:** System fully handed over to Chleo's team, operating autonomously ✅

---

## Key Assumptions

1. **SerpApi scraping success rate:** Assumes >70% of target URLs are scrapable. JavaScript-heavy sites will fall back to snippet analysis.
2. **Team adoption:** Assumes 2 team members (1 senior SEO analyst + 1 account manager) are primary users.
3. **Keyword stability:** The watchlist changes rarely — assume 5–10% keyword turnover per month.
4. **No in-house developer:** Timeline assumes external setup by a consultant. With an in-house developer, Phase 0–1 can be compressed by ~30%.
5. **Tableau license:** Assumes Tableau Public (free) for the pilot, upgrading to Tableau Creator if the team wants to publish internally.

---

## Risks & Contingencies

| Risk | Impact on Timeline | Contingency |
|---|---|---|
| SerpApi scraping blocks | +1 week | Switch to ScaleSerp or Brightdata; adjust scraping frequency |
| LLM output quality too low | +1 week | Upgrade from Haiku to Sonnet; refine prompts |
| Team resistance to adoption | +2 weeks | Add 1 extra training session; start with 1 champion user |
| Scope creep (client requests) | +1–3 weeks | Lock MVP scope; document v2 backlog separately |
| API key configuration issues | +2–3 days | Allocate buffer in Phase 0; use .env.example template |
