\# Agentic AI Research Assistant — Architecture



\## 1. System Overview



The Agentic AI Research Assistant is a multi-stage AI research system designed to transform a natural-language research question into a structured, evidence-backed report.



The application uses \*\*LangGraph\*\* to orchestrate specialized agents and \*\*Google Gemini with Google Search grounding\*\* for AI reasoning and web-based research.



```text

&#x20;                        ┌──────────────────────┐

&#x20;                        │      User Query      │

&#x20;                        └──────────┬───────────┘

&#x20;                                   │

&#x20;                                   ▼

&#x20;                        ┌──────────────────────┐

&#x20;                        │    Input Validation  │

&#x20;                        └──────────┬───────────┘

&#x20;                                   │

&#x20;                                   ▼

&#x20;                        ┌──────────────────────┐

&#x20;                        │    Planner Agent     │

&#x20;                        │                      │

&#x20;                        │ Sub-questions        │

&#x20;                        │ Key research topics   │

&#x20;                        └──────────┬───────────┘

&#x20;                                   │

&#x20;                                   ▼

&#x20;                        ┌──────────────────────┐

&#x20;                        │   Search Agent       │

&#x20;                        │                      │

&#x20;                        │ Gemini + Google      │

&#x20;                        │ Search Grounding     │

&#x20;                        └──────────┬───────────┘

&#x20;                                   │

&#x20;                        ┌──────────┴───────────┐

&#x20;                        │                      │

&#x20;                        ▼                      ▼

&#x20;                 Normal Research        Deep Research

&#x20;                        │                      │

&#x20;                        │              Multiple research

&#x20;                        │                 passes

&#x20;                        │                      │

&#x20;                        └──────────┬───────────┘

&#x20;                                   │

&#x20;                                   ▼

&#x20;                        ┌──────────────────────┐

&#x20;                        │ Evidence Processing  │

&#x20;                        │ \& Source Deduplication│

&#x20;                        └──────────┬───────────┘

&#x20;                                   │

&#x20;                                   ▼

&#x20;                        ┌──────────────────────┐

&#x20;                        │  Verification Agent  │

&#x20;                        │                      │

&#x20;                        │ Verdict              │

&#x20;                        │ Confidence           │

&#x20;                        │ Flagged claims       │

&#x20;                        │ Source relevance     │

&#x20;                        └──────────┬───────────┘

&#x20;                                   │

&#x20;                                   ▼

&#x20;                        ┌──────────────────────┐

&#x20;                        │  Report Writer Agent │

&#x20;                        └──────────┬───────────┘

&#x20;                                   │

&#x20;                                   ▼

&#x20;                        ┌──────────────────────┐

&#x20;                        │    Final Report      │

&#x20;                        │                      │

&#x20;                        │ Markdown / PDF       │

&#x20;                        └──────────────────────┘

```



\---



\## 2. Core Components



\### Streamlit Application



\*\*File:\*\* `app.py`



The Streamlit application provides the user-facing interface.



Responsibilities include:



\* Research question input

\* Research mode selection

\* Input validation

\* Pipeline progress display

\* Research metrics

\* Verification results

\* Final report display

\* Source display

\* Markdown export

\* PDF export

\* Research history interface



The application does not contain the complete research logic itself. Instead, it invokes the LangGraph workflow.



\---



\## 3. LangGraph Workflow



\*\*File:\*\* `graph.py`



LangGraph is responsible for orchestrating the research pipeline.



The workflow connects the major processing stages:



```text

START

&#x20; │

&#x20; ▼

Planner

&#x20; │

&#x20; ▼

Search / Research

&#x20; │

&#x20; ▼

Verification

&#x20; │

&#x20; ▼

Report Writer

&#x20; │

&#x20; ▼

END

```



The shared research state is passed between the nodes.



This allows each agent to focus on a specific responsibility while maintaining a consistent workflow state.



\---



\## 4. Shared Research State



\*\*File:\*\* `state.py`



The application uses a structured `ResearchState` object to maintain information throughout the pipeline.



The state contains information such as:



```text

main\_question

deep\_research

sub\_questions

key\_topics

findings

verifications

final\_report

```



\### State Flow



```text

User Question

&#x20;    │

&#x20;    ▼

main\_question

&#x20;    │

&#x20;    ▼

sub\_questions

&#x20;    │

&#x20;    ▼

findings

&#x20;    │

&#x20;    ▼

verifications

&#x20;    │

&#x20;    ▼

final\_report

```



This shared state allows the output of one stage to become the input for the next stage.



\---



\# 5. Planner Agent



\*\*File:\*\* `agents/planner.py`



The Planner Agent converts the user's main research question into focused research tasks.



\### Responsibilities



\* Understand the research question

\* Identify important topics

\* Generate focused sub-questions

\* Prepare the research plan



Conceptually:



```text

Main Question

&#x20;     │

&#x20;     ▼

&#x20;  Planner

&#x20;     │

&#x20;     ├── Sub-question 1

&#x20;     ├── Sub-question 2

&#x20;     ├── Sub-question 3

&#x20;     └── ...

```



The planner can produce multiple sub-questions depending on the research topic.



\---



\# 6. Search / Research Agent



\*\*File:\*\* `agents/searcher.py`



The Search Agent performs web-grounded research using Gemini and Google Search grounding.



\### Responsibilities



\* Research each sub-question

\* Gather evidence

\* Extract useful findings

\* Collect source references

\* Support normal and deep research modes



The collected evidence is passed forward for verification.



\---



\# 7. Normal Research Mode



Normal mode performs one research pass for each generated sub-question.



```text

Sub-question

&#x20;    │

&#x20;    ▼

Research Pass

&#x20;    │

&#x20;    ▼

Finding + Sources

```



This mode provides a faster research workflow while still using web-grounded evidence.



\---



\# 8. Deep Research Mode



Deep Research performs multiple independent research passes for each sub-question.



```text

&#x20;                Sub-question

&#x20;                      │

&#x20;            ┌─────────┴─────────┐

&#x20;            ▼                   ▼

&#x20;      Research Pass 1     Research Pass 2

&#x20;            │                   │

&#x20;            └─────────┬─────────┘

&#x20;                      ▼

&#x20;               Combine Findings

&#x20;                      │

&#x20;                      ▼

&#x20;               Deduplicate Sources

&#x20;                      │

&#x20;                      ▼

&#x20;                 Verification

```



The goal is to increase evidence coverage and reduce dependence on a single research pass.



\---



\# 9. Source Collection and Deduplication



The research stage collects source references from the grounded search results.



The system then processes the sources to reduce duplicate references.



Conceptually:



```text

Research Results

&#x20;     │

&#x20;     ▼

Source Collection

&#x20;     │

&#x20;     ▼

Duplicate Detection

&#x20;     │

&#x20;     ▼

Unique Sources

```



This allows the final report and UI to present a cleaner evidence set.



\---



\# 10. Verification Agent



\*\*File:\*\* `agents/verifier.py`



The Verification Agent evaluates the research findings against the collected evidence.



It produces structured verification information including:



\* `verdict`

\* `confidence`

\* `flagged\_claims`

\* `source\_relevance\_notes`

\* `agreement\_notes`

\* `sub\_question`



\### Verification Flow



```text

Research Finding

&#x20;     │

&#x20;     ▼

Evidence Review

&#x20;     │

&#x20;     ▼

Verification

&#x20;     │

&#x20;     ├── Verdict

&#x20;     ├── Confidence

&#x20;     ├── Flagged Claims

&#x20;     ├── Source Relevance

&#x20;     └── Agreement Notes

```



The verification stage is designed to identify findings that may require additional evidence or careful interpretation.



\---



\# 11. Report Writer Agent



\*\*File:\*\* `agents/report\_writer.py`



The Report Writer transforms the processed research and verification information into a structured final report.



The report can include:



\* Title

\* Executive summary

\* Research findings

\* Evidence

\* Verification information

\* Sources



The generated report is then presented through the Streamlit interface.



\---



\# 12. Research History



\*\*File:\*\* `history.py`



The application stores completed research sessions locally using SQLite.



Research history allows users to access previous research results without rebuilding the research process from scratch.



Conceptually:



```text

Completed Research

&#x20;      │

&#x20;      ▼

&#x20;  Save Result

&#x20;      │

&#x20;      ▼

&#x20;SQLite Database

&#x20;      │

&#x20;      ▼

&#x20;Retrieve Previous Research

```



The local database is intended for development/local usage and is excluded from version control.



\---



\# 13. Input Validation



The application validates the research question before starting the research pipeline.



Examples of invalid inputs include:



\* Empty questions

\* Extremely short inputs

\* Common conversational messages such as greetings



This prevents unnecessary Gemini and search calls for inputs that are not meaningful research requests.



```text

User Input

&#x20;   │

&#x20;   ▼

Validation

&#x20;   │

&#x20;┌──┴───────────────┐

&#x20;│                  │

Invalid            Valid

&#x20;│                  │

&#x20;▼                  ▼

Warning          Research

&#x20;                 Pipeline

```



\---



\# 14. Error Handling



The application includes error handling around the research execution process.



If a pipeline/API operation fails, the UI can display an appropriate error message instead of terminating unexpectedly.



This is particularly important because the application depends on external AI and search services.



\---



\# 15. Report Export



The final report can be exported in multiple formats.



```text

&#x20;                Final Report

&#x20;                     │

&#x20;            ┌────────┴────────┐

&#x20;            ▼                 ▼

&#x20;       Markdown              PDF

```



PDF generation is handled inside the Streamlit application using FPDF.



\---



\# 16. Security



API credentials are loaded through environment variables.



The application uses:



```text

GEMINI\_API\_KEY

```



The `.env` file is excluded through `.gitignore`.



The repository also excludes development-only resources such as:



\* Virtual environments

\* Python cache files

\* Local databases

\* Environment files

\* Logs

\* IDE configuration files



API credentials should never be committed to source control.



\---



\# 17. Technology Architecture



```text

┌─────────────────────────────────────────────┐

│                 Streamlit UI                │

├─────────────────────────────────────────────┤

│              LangGraph Workflow             │

├──────────────┬──────────────┬───────────────┤

│   Planner    │   Searcher   │   Verifier    │

├──────────────┴──────────────┴───────────────┤

│              Report Writer                  │

├─────────────────────────────────────────────┤

│          Google Gemini + Search             │

├─────────────────────────────────────────────┤

│        SQLite / Local Research History      │

└─────────────────────────────────────────────┘

```



\---



\# 18. Design Principles



The project follows several principles:



\### Separation of Responsibilities



Each agent has a clearly defined role instead of combining planning, research, verification, and reporting into a single prompt.



\### Evidence-Grounded Research



Research results are based on web-grounded evidence rather than relying only on model-generated knowledge.



\### Verification Before Reporting



Findings pass through a dedicated verification stage before final report generation.



\### Configurable Research Depth



Users can choose between normal and deep research modes.



\### API Efficiency



Invalid or low-information requests are rejected before expensive research operations are started.



\### Reproducible Workflow



The LangGraph-based pipeline provides a structured sequence of research stages.



\---



\# 19. Current Pipeline



The current implementation follows:



```text

Input Validation

&#x20;      ↓

Planner

&#x20;      ↓

Search / Research

&#x20;      ↓

Source Deduplication

&#x20;      ↓

Verification

&#x20;      ↓

Report Writer

&#x20;      ↓

Final Report

&#x20;      ↓

Markdown / PDF Export

```



For Deep Research:



```text

Input Validation

&#x20;      ↓

Planner

&#x20;      ↓

Multiple Research Passes

&#x20;      ↓

Evidence Combination

&#x20;      ↓

Source Deduplication

&#x20;      ↓

Verification

&#x20;      ↓

Report Writer

&#x20;      ↓

Final Report

```



\---



\# 20. Future Architecture Improvements



Potential future improvements include:



\* Parallel execution of independent research tasks

\* More advanced source-quality evaluation

\* Claim-level citation mapping

\* Additional search providers

\* More sophisticated evidence aggregation

\* Persistent cloud-based research history

\* Authentication and user management

\* Distributed agent execution

\* Deployment on cloud infrastructure



\---



\## Summary



The Agentic AI Research Assistant uses a structured multi-agent architecture to turn research questions into evidence-backed reports.



The core workflow is:



\*\*Planner → Search → Verify → Report\*\*



with LangGraph providing workflow orchestration, Gemini providing AI capabilities, Google Search grounding providing web evidence, and Streamlit providing the interactive application interface.



