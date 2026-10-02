from langgraph.graph import StateGraph, END

from state import ResearchState
from agents.planner import plan_research
from agents.searcher import research_all
from agents.verifier import verify_all
from agents.report_writer import write_report


def planner_node(state: ResearchState) -> ResearchState:
    """
    LangGraph node: runs the Research Planner Agent.
    Reads: state["main_question"]
    Writes: state["sub_questions"], state["key_topics"]
    """
    plan = plan_research(state["main_question"])

    state["sub_questions"] = plan["sub_questions"]
    state["key_topics"] = plan["key_topics"]

    return state


def search_node(state: ResearchState) -> ResearchState:
    """
    LangGraph node: runs the Research/Search Agent.
    Reads: state["sub_questions"]
    Writes: state["findings"]
    """
    findings = research_all(
    state["sub_questions"],
    state["deep_research"],
)

    state["findings"] = findings

    return state


def verify_node(state: ResearchState) -> ResearchState:
    """
    LangGraph node: runs the Fact/Source Verification Agent.
    Reads: state["findings"]
    Writes: state["verifications"]
    """
    verifications = verify_all(state["findings"])

    state["verifications"] = verifications

    return state


def report_node(state: ResearchState) -> ResearchState:
    """
    LangGraph node: runs the Report Writer Agent.
    Reads: state["main_question"], state["findings"], state["verifications"]
    Writes: state["final_report"]
    """
    report = write_report(
        state["main_question"],
        state["findings"],
        state["verifications"],
    )

    state["final_report"] = report

    return state


def build_graph():
    """
    Builds and compiles the LangGraph StateGraph:
    START -> planner_node -> search_node -> verify_node -> report_node -> END
    """
    graph_builder = StateGraph(ResearchState)

    graph_builder.add_node("planner", planner_node)
    graph_builder.add_node("search", search_node)
    graph_builder.add_node("verify", verify_node)
    graph_builder.add_node("report", report_node)

    graph_builder.set_entry_point("planner")
    graph_builder.add_edge("planner", "search")
    graph_builder.add_edge("search", "verify")
    graph_builder.add_edge("verify", "report")
    graph_builder.add_edge("report", END)

    return graph_builder.compile()