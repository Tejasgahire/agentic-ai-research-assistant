from graph import build_graph

app = build_graph()

initial_state = {
    "main_question": "What are the economic effects of remote work on urban housing markets?",
    "sub_questions": [],
    "key_topics": [],
    "findings": [],
}

print("Invoking graph...")
final_state = app.invoke(initial_state)

print("\nFinal main_question:")
print(final_state["main_question"])

print("\nSub-questions:")
for sq in final_state["sub_questions"]:
    print(f"  - {sq}")

print("\nKey topics:")
for kt in final_state["key_topics"]:
    print(f"  - {kt}")

print("\nFindings:")
for f in final_state["findings"]:
    print(f"\nQ: {f['sub_question']}")
    print(f"Summary: {f['summary'][:150]}...")
    print(f"Sources found: {len(f['sources'])}")