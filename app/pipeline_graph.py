from collections.abc import Callable
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.config import get_settings
from app.metrics import readability_metrics


Simplifier = Callable[[str, str, str | None], str]


class PipelineState(TypedDict, total=False):
    source_text: str
    language: str
    simplified_text: str
    feedback: str | None
    attempts: int
    source_metrics: dict
    output_metrics: dict
    error: str


def create_pipeline(simplifier: Simplifier):
    """Build the simplify/evaluate/self-correct workflow around a supplied model."""

    def validate(state: PipelineState) -> PipelineState:
        text = state.get("source_text", "").strip()
        language = state.get("language", "").strip()
        if not text:
            raise ValueError("source_text must not be empty")
        if not language:
            raise ValueError("language must not be empty")
        return {
            **state,
            "source_text": text,
            "language": language,
            "source_metrics": readability_metrics(text),
            "attempts": 0,
            "feedback": None,
        }

    def simplify(state: PipelineState) -> PipelineState:
        attempts = state.get("attempts", 0) + 1
        result = simplifier(
            state["source_text"], state["language"], state.get("feedback")
        ).strip()
        if not result:
            raise ValueError("The simplifier returned empty text")
        return {
            **state,
            "simplified_text": result,
            "output_metrics": readability_metrics(result),
            "attempts": attempts,
        }

    def evaluate(state: PipelineState) -> PipelineState:
        source_length = state["source_metrics"]["avg_words_per_sentence"]
        output_length = state["output_metrics"]["avg_words_per_sentence"]
        if output_length < source_length or state["attempts"] >= get_settings().max_pipeline_attempts:
            return {**state, "feedback": None}
        return {
            **state,
            "feedback": "Use shorter sentences and simpler wording while preserving meaning.",
        }

    def route(state: PipelineState) -> str:
        if state.get("feedback") and state["attempts"] < get_settings().max_pipeline_attempts:
            return "simplify"
        return END

    graph = StateGraph(PipelineState)
    graph.add_node("validate", validate)
    graph.add_node("simplify", simplify)
    graph.add_node("evaluate", evaluate)
    graph.add_edge(START, "validate")
    graph.add_edge("validate", "simplify")
    graph.add_edge("simplify", "evaluate")
    graph.add_conditional_edges("evaluate", route)
    return graph.compile()
