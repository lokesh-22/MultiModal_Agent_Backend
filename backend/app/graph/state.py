from typing import TypedDict


class AgentState(TypedDict, total=False):

    user_query: str

    session_id: str

    request_id: str

    uploaded_files: list

    uploaded_file_metadata: dict

    extracted_contents: dict

    source_documents: list

    combined_context: str

    intent: str

    confidence: float

    needs_followup: bool

    followup_question: str

    execution_plan: list

    tool_results: dict

    plan_routing: dict

    reasoning_trace: list

    final_response: str

    event_bus: object