from history import init_db, save_research, get_all_history, get_history_by_id

init_db()

sample_final_state = {
    "main_question": "What are the economic effects of remote work on urban housing markets?",
    "sub_questions": ["How has remote work influenced housing demand?"],
    "key_topics": ["remote work", "urban housing"],
    "findings": [
        {
            "sub_question": "How has remote work influenced housing demand?",
            "summary": "This is a test summary.",
            "sources": [{"title": "Test Source", "url": "https://example.com"}],
        }
    ],
    "verifications": [
        {
            "sub_question": "How has remote work influenced housing demand?",
            "verdict": "supported",
            "confidence": "high",
            "flagged_claims": [],
            "source_relevance_notes": "Relevant.",
            "agreement_notes": "N/A",
        }
    ],
    "final_report": {
        "title": "Test Report",
        "executive_summary": "This is a test executive summary.",
        "sections": [{"heading": "Test Section", "content": "Test content."}],
        "confidence_notes": "Well supported.",
        "sources": [{"title": "Test Source", "url": "https://example.com"}],
    },
}

new_id = save_research(sample_final_state["main_question"], sample_final_state)
print(f"Saved research with id: {new_id}")

print("\nAll history:")
history_list = get_all_history()
for item in history_list:
    print(f"  [{item['id']}] {item['question']} — {item['created_at']}")

print(f"\nRetrieving full record for id {new_id}:")
retrieved = get_history_by_id(new_id)
print(retrieved["final_report"]["title"])
print(retrieved["final_report"]["executive_summary"])