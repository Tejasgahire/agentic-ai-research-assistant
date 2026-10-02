from graph import build_graph

app = build_graph()

initial_state = {
    "main_question": "What are the economic effects of remote work on urban housing markets?",
    "sub_questions": [],
    "key_topics": [],
    "findings": [],
    "verifications": [],
    "final_report": {},
}

print("Invoking full graph (planner -> search -> verify -> report)...")
final_state = app.invoke(initial_state)

print("\nMain question:")
print(final_state["main_question"])

print("\nSub-questions:")
for sq in final_state["sub_questions"]:
    print(f"  - {sq}")

print("\n--- Findings + Verifications ---")
for finding, verification in zip(final_state["findings"], final_state["verifications"]):
    print(f"\nQ: {finding['sub_question']}")
    print(f"Summary: {finding['summary'][:150]}...")
    print(f"Sources: {len(finding['sources'])}")
    print(f"Verdict: {verification['verdict']} (confidence: {verification['confidence']})")

report = final_state["final_report"]
print("\n\n=== FINAL REPORT ===")
print(f"\nTitle: {report['title']}")
print(f"\nExecutive Summary:\n{report['executive_summary']}")

print("\nSections:")
for section in report["sections"]:
    print(f"\n## {section['heading']}")
    print(section["content"])

print(f"\nConfidence Notes:\n{report['confidence_notes']}")

print("\nSources:")
for src in report["sources"]:
    print(f"  - {src['title']}: {src['url']}")