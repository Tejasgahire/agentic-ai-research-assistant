import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from agents.utils import call_with_retry

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

_search_tool = types.Tool(google_search=types.GoogleSearch())


def research_sub_question(sub_question: str) -> dict:
    """
    Standard research pass for a single sub-question.
    Uses Gemini with Google Search grounding.
    """
    response = call_with_retry(
        _client.models.generate_content,
        model="gemini-2.5-flash",
        contents=(
            f"Research this question using current web information and give a "
            f"concise, factual summary (4-6 sentences). "
            f"Prefer reliable and relevant sources:\n\n{sub_question}"
        ),
        config=types.GenerateContentConfig(
            tools=[_search_tool],
        ),
    )

    summary = response.text.strip()

    sources = []

    try:
        grounding = response.candidates[0].grounding_metadata

        if grounding and grounding.grounding_chunks:
            for chunk in grounding.grounding_chunks:
                if chunk.web:
                    sources.append({
                        "title": chunk.web.title,
                        "url": chunk.web.uri,
                    })

    except (AttributeError, IndexError):
        pass

    return {
        "sub_question": sub_question,
        "summary": summary,
        "sources": sources,
    }


def deep_research_sub_question(sub_question: str) -> dict:
    """
    Performs an additional independent research pass for Deep Research mode.

    The goal is to look for corroborating evidence, contrasting information,
    limitations, and additional reliable sources.
    """

    response = call_with_retry(
        _client.models.generate_content,
        model="gemini-2.5-flash",
        contents=(
            f"Perform a deeper independent research pass for this question "
            f"using current web information.\n\n"
            f"Question: {sub_question}\n\n"
            f"Look specifically for:\n"
            f"- additional reliable sources\n"
            f"- evidence that corroborates or challenges common claims\n"
            f"- important statistics or recent developments when available\n"
            f"- disagreements, limitations, or uncertainty\n\n"
            f"Give a factual synthesis in 5-8 sentences. "
            f"Do not invent facts or sources."
        ),
        config=types.GenerateContentConfig(
            tools=[_search_tool],
        ),
    )

    summary = response.text.strip()

    sources = []

    try:
        grounding = response.candidates[0].grounding_metadata

        if grounding and grounding.grounding_chunks:
            for chunk in grounding.grounding_chunks:
                if chunk.web:
                    sources.append({
                        "title": chunk.web.title,
                        "url": chunk.web.uri,
                    })

    except (AttributeError, IndexError):
        pass

    return {
        "sub_question": sub_question,
        "summary": summary,
        "sources": sources,
    }


def research_all(
    sub_questions: list,
    deep_research: bool = False,
) -> list:
    """
    Runs research for all sub-questions.

    Normal mode:
        One research pass per sub-question.

    Deep Research mode:
        Two independent research passes per sub-question.
        Their summaries and sources are combined into one finding so that
        the existing verification and report stages can remain unchanged.
    """

    findings = []

    for sq in sub_questions:

        # ------------------------------------------------------------
        # NORMAL RESEARCH
        # ------------------------------------------------------------
        primary_result = research_sub_question(sq)

        if not deep_research:
            findings.append(primary_result)
            continue

        # ------------------------------------------------------------
        # DEEP RESEARCH
        # ------------------------------------------------------------
        secondary_result = deep_research_sub_question(sq)

        combined_summary = (
            f"Primary research:\n"
            f"{primary_result['summary']}\n\n"
            f"Additional independent research:\n"
            f"{secondary_result['summary']}"
        )

        combined_sources = (
            primary_result.get("sources", [])
            + secondary_result.get("sources", [])
        )

        # Remove duplicate URLs while preserving order.
        unique_sources = []
        seen_urls = set()

        for source in combined_sources:
            url = source.get("url")

            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_sources.append(source)

        findings.append({
            "sub_question": sq,
            "summary": combined_summary,
            "sources": unique_sources,
        })

    return findings