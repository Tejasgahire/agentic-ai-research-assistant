from typing import TypedDict, List, Literal


class Source(TypedDict):
    title: str
    url: str


class Finding(TypedDict):
    sub_question: str
    summary: str
    sources: List[Source]


class Verification(TypedDict):
    sub_question: str
    verdict: Literal["supported", "partially_supported", "unsupported", "insufficient_sources"]
    confidence: Literal["high", "medium", "low"]
    flagged_claims: List[str]
    source_relevance_notes: str
    agreement_notes: str


class ReportSection(TypedDict):
    heading: str
    content: str


class FinalReport(TypedDict):
    title: str
    executive_summary: str
    sections: List[ReportSection]
    confidence_notes: str
    sources: List[Source]


class ResearchState(TypedDict):
    main_question: str
    deep_research: bool
    sub_questions: List[str]
    key_topics: List[str]
    findings: List[Finding]
    verifications: List[Verification]
    final_report: FinalReport