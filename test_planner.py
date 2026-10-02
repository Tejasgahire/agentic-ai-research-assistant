from agents.planner import plan_research

question = "What are the economic effects of remote work on urban housing markets?"

plan = plan_research(question)

print("Main question:")
print(plan["main_question"])
print("\nSub-questions:")
for i, sq in enumerate(plan["sub_questions"], 1):
    print(f"  {i}. {sq}")
print("\nKey topics:")
for topic in plan["key_topics"]:
    print(f"  - {topic}")