from graph import planner_node, search_node

initial_state = {
    "main_question": "What are the economic effects of remote work on urban housing markets?",
    "sub_questions": [],
    "key_topics": [],
    "findings": [],
}

print("Running planner_node...")
state = planner_node(initial_state)
print("\nSub-questions from planner:")
for sq in state["sub_questions"]:
    print(f"  - {sq}")

print("\nRunning search_node...")
state = search_node(state)

print("\nFindings from search_node:")
for f in state["findings"]:
    print(f"\nQ: {f['sub_question']}")
    print(f"Summary: {f['summary'][:150]}...")
    print(f"Sources found: {len(f['sources'])}")