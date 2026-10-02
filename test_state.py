from state import ResearchState, Finding, Source, Verification, FinalReport, ReportSection

sample_state: ResearchState = {
    "main_question": "Test question?",
    "sub_questions": ["Sub question 1?", "Sub question 2?"],
    "key_topics": ["topic1", "topic2"],
    "findings": [
        {
            "sub_question": "Sub question 1?",
            "summary": "This is a test summary.",
            "sources": [
                {"title": "Example Source", "url": "https://example.com"}
            ],
        }
    ],
    "verifications": [
        {
            "sub_question": "Sub question 1?",
            "verdict": "supported",
            "confidence": "medium",
            "flagged_claims": [],
            "source_relevance_notes": "Source is relevant.",
            "agreement_notes": "Only one source; no conflict to assess.",
        }
    ],
    "final_report": {
        "title": "Test Report Title",
        "executive_summary": "This is a short test summary of the findings.",
        "sections": [
            {"heading": "Test Section", "content": "This is test section content."}
        ],
        "confidence_notes": "1 of 1 findings were well-supported.",
        "sources": [
            {"title": "Example Source", "url": "https://example.com"}
        ],
    },
}

print("ResearchState with final_report constructed successfully.")
print(sample_state)