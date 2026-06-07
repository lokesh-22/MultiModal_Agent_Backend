from langgraph.graph import StateGraph

from app.graph.state import AgentState

from app.graph.nodes.input_processor import (
    input_processor
)

from app.graph.nodes.content_extractor import (
    content_extractor
)

from app.graph.nodes.context_builder import (
    context_builder
)

from app.graph.nodes.intent_detector import (
    intent_detector
)

from app.graph.nodes.ambiguity_checker import (
    ambiguity_checker
)

from app.graph.nodes.planner import (
    planner
)

from app.graph.nodes.tool_executor import (
    tool_executor
)

from app.graph.nodes.response_generator import (
    response_generator
)

from app.graph.nodes.followup_node import (
    followup_node
)

def build_graph():

    graph = StateGraph(
        AgentState
    )

    # Nodes
    graph.add_node(
        "input_processor",
        input_processor
    )

    graph.add_node(
        "content_extractor",
        content_extractor
    )

    graph.add_node(
        "context_builder",
        context_builder
    )

    graph.add_node(
        "intent_detector",
        intent_detector
    )

    graph.add_node("ambiguity_checker", ambiguity_checker)
    graph.add_node("planner", planner)
    graph.add_node("tool_executor", tool_executor)
    graph.add_node("response_generator", response_generator)
    graph.add_node("followup_node", followup_node)

    # Entry Point
    graph.set_entry_point(
        "input_processor"
    )

    # Edges
    graph.add_edge(
        "input_processor",
        "content_extractor"
    )

    graph.add_edge(
        "content_extractor",
        "context_builder"
    )

    graph.add_edge(
        "context_builder",
        "intent_detector"
    )

    graph.add_edge("intent_detector", "ambiguity_checker")

    graph.add_conditional_edges(
        "ambiguity_checker",
        lambda state: "followup" if state["needs_followup"] else "planner",
        {
            "followup": "followup_node",
            "planner": "planner",
        },
    )

    graph.add_edge("planner", "tool_executor")
    graph.add_edge("tool_executor", "response_generator")

    graph.set_finish_point("followup_node")
    graph.set_finish_point("response_generator")
    return graph.compile()