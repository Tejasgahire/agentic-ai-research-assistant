import os
import json
from dotenv import load_dotenv
from google import genai

from agents.utils import call_with_retry

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

_REPORT_WRITER_SYSTEM_PROMPT = """You are a Report Writer Agent.

You will be given:
- A main research question
- A list of findings (sub_question, summary, sources)
- A list of verification results (sub_question, verdict, confidence, flagged_claims,
  source_relevance_notes, agreement_notes)

Your job is to write a clear, well-organized final research report that answers the main
question, using the findings as evidence.

CRITICAL RULES:
1. You MUST take verification results into account. Do not present findings with a verdict
   of "unsupported" or "partially_supported" as if they were fully certain. Use appropriate
   hedging language (e.g. "preliminary evidence suggests", "one source claims, though this
   is not well-corroborated") for anything not marked "supported" with "high" or "medium"
   confidence.
2. If a finding has flagged_claims, do not repeat those specific claims as fact in the report.
   Either omit them or clearly caveat them.
3. Organize the report into logical thematic sections, not just one section per sub-question restated
   verbatim.
4. Write a short executive summary that directly answers the main question.
5. Write a confidence_notes field summarizing how many findings were well-supported vs. not,
   in plain language.
6. Collect all unique sources across all findings into the final sources list (deduplicate by url).

Respond ONLY with valid JSON, no markdown formatting, no code fences, no explanation outside the JSON.

JSON schema:
{
  "title": "<short descriptive report title>",
  "executive_summary": "<2-4 sentence direct answer to the main question>",
  "sections": [
    {"heading": "<section heading>", "content": "<synthesized prose for this section>"}
  ],
  "confidence_notes": "<plain-language summary of overall confidence/limitations>",
  "sources": [
    {"title": "<source title>", "url": "<source url>"}
  ]
}
"""


def write_report(main_question: str, findings: list, verifications: list) -> dict:
    """
    Takes the main question, findings, and verifications, and returns a
    structured final report dict matching the FinalReport schema.
    """
    payload = {
        "main_question": main_question,
        "findings": findings,
        "verifications": verifications,
    }

    prompt = (
        f"{_REPORT_WRITER_SYSTEM_PROMPT}\n\n"
        f"Input data:\n{json.dumps(payload, indent=2)}"
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
        report = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Report Writer did not return valid JSON:\n{raw_text}") from e

    return report