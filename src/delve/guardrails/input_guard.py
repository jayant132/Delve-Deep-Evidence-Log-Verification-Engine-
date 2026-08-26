import logging
import re

logger = logging.getLogger(__name__)

INJECTION_PATTERNS = [
    r"ignore (all |previous |the )?(instructions|prompt)",
    r"you are now",
    r"disregard (all |previous |the )?(instructions|rules)",
    r"system prompt",
    r"act as (a |an )?(different|new)",
    r"\bDAN\b",
    r"</?(system|instruction)s?>",
]
_compiled_patterns = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def scan_for_injection(text: str) -> list[str]:
    return [p.pattern for p in _compiled_patterns if p.search(text)]


def check_incident_input(title: str, description: str) -> None:
    matches = scan_for_injection(f"{title}\n{description}")
    if matches:
        logger.warning("Possible prompt injection pattern(s) detected: %s", matches)
