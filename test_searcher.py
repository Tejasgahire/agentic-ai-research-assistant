from agents.searcher import research_sub_question

sub_question = "How has remote work influenced demand for urban housing?"

result = research_sub_question(sub_question)

print("Sub-question:")
print(result["sub_question"])

print("\nSummary:")
print(result["summary"])

print("\nSources:")
for src in result["sources"]:
    print(f"  - {src['title']}: {src['url']}")