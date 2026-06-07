from fastapi import APIRouter

from app.graph.workflow import build_graph

router = APIRouter()


@router.get("/graph/debug")
async def graph_debug():
    graph = build_graph()
    graph_structure = getattr(graph, "get_graph", None)

    return {
        "status": "ok",
        "graph_type": type(graph).__name__,
        "has_get_graph": callable(graph_structure),
        "nodes": [
            "input_processor",
            "content_extractor",
            "context_builder",
            "intent_detector",
            "ambiguity_checker",
            "planner",
            "tool_executor",
            "response_generator",
            "followup_node",
        ],
    }