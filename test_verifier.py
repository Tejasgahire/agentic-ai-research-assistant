from agents.verifier import verify_finding

sample_finding = {
    "sub_question": "How has remote work influenced demand for urban housing?",
    "summary": (
        "Remote work has significantly reduced demand for urban housing, causing city "
        "populations to fall by exactly 47.3% since 2020, according to studies. Nearly "
        "everyone who can work remotely has already left major cities permanently."
    ),
    "sources": [
        {"title": "The Residentially Blog", "url": "https://theresidentially.com"},
        {"title": "Harvard Joint Center for Housing Studies", "url": "https://harvard.edu"},
    ],
}

result = verify_finding(sample_finding)

print("Verdict:", result["verdict"])
print("Confidence:", result["confidence"])
print("\nFlagged claims:")
for claim in result["flagged_claims"]:
    print(f"  - {claim}")
print("\nSource relevance notes:")
print(result["source_relevance_notes"])
print("\nAgreement notes:")
print(result["agreement_notes"])