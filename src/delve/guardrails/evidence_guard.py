def check_evidence_grounding(root_cause: dict, all_observed_facts: list[str]) -> list[str]:
    """Returns supporting_evidence claims that don't closely match any real
    observed fact — a lightweight substring check, not NLP-based."""
    flagged = []
    for claim in root_cause.get("supporting_evidence", []):
        if not any(
            claim[:30].lower() in fact.lower() or fact[:30].lower() in claim.lower()
            for fact in all_observed_facts
        ):
            flagged.append(claim)
    return flagged
