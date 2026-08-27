import asyncio

from delve.agents.investigation_service import run_investigation
from delve.agents.triage_service import run_triage
from delve.evals.dataset import EVAL_CASES

CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}


async def run_case(case: dict) -> dict:
    incident_text = f"Title: {case['title']}\nDescription: {case['description']}"
    await run_triage(incident_text)
    results = await run_investigation(incident_text)
    rca = results["root_cause_analysis"]

    hypothesis = rca.get("root_cause_hypothesis", "").lower()
    keyword_hits = sum(1 for kw in case["expected_root_cause_keywords"] if kw.lower() in hypothesis)
    keyword_score = keyword_hits / len(case["expected_root_cause_keywords"])

    historical_ok = case["expected_historical_match"].lower() in rca.get("historical_precedent", "").lower()

    confidence_ok = CONFIDENCE_RANK.get(rca.get("confidence", "low"), 0) >= CONFIDENCE_RANK[case["expected_min_confidence"]]

    return {
        "case_id": case["case_id"],
        "keyword_score": round(keyword_score, 2),
        "historical_match_found": historical_ok,
        "confidence_met": confidence_ok,
        "passed": keyword_score >= 0.5 and historical_ok and confidence_ok,
    }


async def main():
    results = [await run_case(c) for c in EVAL_CASES]
    passed = sum(1 for r in results if r["passed"])
    for r in results:
        print(r)
    print(f"\n{passed}/{len(results)} cases passed")


asyncio.run(main())
