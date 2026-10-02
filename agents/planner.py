import os
import json
from dotenv import load_dotenv
from google import genai

from agents.utils import call_with_retry

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

_PLANNER_SYSTEM_PROMPT = """You are a Research Planner Agent.

Given a user's research question, break it down into a structured research plan.

Respond ONLY with valid JSON, no markdown formatting, no code fences, no explanation.

JSON schema:
{
  "main_question": "<the original question, unchanged>",
  "sub_questions": ["<3 to 6 focused sub-questions>"],
  "key_topics": ["<3 to 6 short topics or entities to search for>"]
}
"""


def plan_research(question: str) -> dict:
    """
    Takes a research question and returns a structured research plan.

    If the MAX_SUB_QUESTIONS environment variable is set (e.g. in .env),
    the sub_questions list is trimmed to that many items. This is a
    development-only convenience to reduce Gemini API calls downstream
    (Search + Verify agents each make one call per sub-question).

    If MAX_SUB_QUESTIONS is not set, the full plan is returned unchanged
    (production behavior).
    """
    prompt = f"{_PLANNER_SYSTEM_PROMPT}\n\nUser research question: {question}"

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
        plan = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Planner did not return valid JSON:\n{raw_text}") from e

    max_sub_questions = os.getenv("MAX_SUB_QUESTIONS")
    if max_sub_questions:
        limit = int(max_sub_questions)
        plan["sub_questions"] = plan["sub_questions"][:limit]

    return plan