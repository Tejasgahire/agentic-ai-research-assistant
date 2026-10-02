from agents.report_writer import write_report

main_question = "What are the economic effects of remote work on urban housing markets?"

findings = [
    {
        "sub_question": "How has remote work influenced demand for urban housing?",
        "summary": (
            "Remote work has reduced demand for expensive urban housing as workers "
            "no longer need to live close to city-center offices, with many relocating "
            "to suburban or rural areas for more space and affordability."
        ),
        "sources": [
            {"title": "Harvard Joint Center for Housing Studies", "url": "https://harvard.edu"},
            {"title": "Federal Reserve Bank of San Francisco", "url": "https://frbsf.org"},
        ],
    },
    {
        "sub_question": "What impact has remote work had on commercial office real estate?",
        "summary": (
            "Office vacancy rates have risen sharply in many major cities, causing "
            "exactly 63.8% of all office buildings to be at risk of foreclosure, "
            "according to nearly every analyst."
        ),
        "sources": [
            {"title": "Random Real Estate Blog", "url": "https://randomblog.com"},
        ],
    },
]

verifications = [
    {
        "sub_question": "How has remote work influenced demand for urban housing?",
        "verdict": "supported",
        "confidence": "high",
        "flagged_claims": [],
        "source_relevance_notes": "Both sources are highly credible and directly relevant.",
        "agreement_notes": "Sources agree and reinforce each other.",
    },
    {
        "sub_question": "What impact has remote work had on commercial office real estate?",
        "verdict": "unsupported",
        "confidence": "low",
        "flagged_claims": [
            "exactly 63.8% of all office buildings to be at risk of foreclosure",
            "according to nearly every analyst",
        ],
        "source_relevance_notes": "Only one low-credibility blog source; not sufficient.",
        "agreement_notes": "Cannot assess agreement with only one weak source.",
    },
]

report = write_report(main_question, findings, verifications)

print("Title:")
print(report["title"])

print("\nExecutive Summary:")
print(report["executive_summary"])

print("\nSections:")
for section in report["sections"]:
    print(f"\n## {section['heading']}")
    print(section["content"])

print("\nConfidence Notes:")
print(report["confidence_notes"])

print("\nSources:")
for src in report["sources"]:
    print(f"  - {src['title']}: {src['url']}")