import os
import json
from dotenv import load_dotenv
from google import genai

from agents.utils import call_with_retry

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

_VERIFIER_SYSTEM_PROMPT = """You are a Fact/Source Verification Agent.

You will be given a sub-question, a summary that was generated to answer it, and a list of
sources (title + url) that were used to produce that summary.

Your job is to CRITICALLY evaluate the summary. Do NOT assume the summary is correct just
because it sounds fluent or confident. Specifically:

1. Judge whether the specific claims in the summary are plausible and reasonably supported,
   given the sub-question and the sources listed (by title/domain — you do not have the full
   page text, so reason about plausibility, specificity, and whether claims go further than
   what such sources would credibly support).
2. Judge whether the sources are actually relevant/related to the sub-question, based on their
   titles and domains.
3. Identify any specific claims in the summary that seem unsupported, overly broad, speculative,
   or suspicious (e.g. oddly specific statistics with no clear source, sweeping generalizations).
4. Note whether the sources appear to agree, conflict, or are too few/homogeneous to tell.
5. If there are zero or very few sources, factor that into your verdict and confidence honestly.

Respond ONLY with valid JSON, no markdown formatting, no code fences, no explanation outside the JSON.

JSON schema:
{
  "verdict": "supported" | "partially_supported" | "unsupported" | "insufficient_sources",
  "confidence": "high" | "medium" | "low",
  "flagged_claims": ["<specific questionable claim>", ...],
  "source_relevance_notes": "<short note>",
  "agreement_notes": "<short note>"
}
"""


def verify_finding(finding: dict) -> dict:
    """
    Takes a single finding dict (sub_question, summary, sources) and returns
    a structured verification result dict.
    """
    sources_text = "\n".join(
        f"- {s.get('title', 'Untitled')}: {s.get('url', 'no-url')}"
        for s in finding.get("sources", [])
    ) or "No sources were provided."

    prompt = (
        f"{_VERIFIER_SYSTEM_PROMPT}\n\n"
        f"Sub-question: {finding['sub_question']}\n\n"
        f"Summary to evaluate:\n{finding['summary']}\n\n"
        f"Sources:\n{sources_text}"
    )

    response = call_with_retry(
        _client.models.generate_content,
        model="gemini-2.5-flash",
        contents=prompt,
    )

    raw_text = response.text.strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:].strip()

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Verifier did not return valid JSON:\n{raw_text}") from e

    result["sub_question"] = finding["sub_question"]

    return result


def verify_all(findings: list) -> list:
    """
    Runs verify_finding on a list of findings.
    Returns a list of verification result dicts.
    """
    verifications = []
    for finding in findings:
        result = verify_finding(finding)
        verifications.append(result)
    return verifications