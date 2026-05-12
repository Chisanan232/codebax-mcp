"""type.get_expected_at_position and type.infer_expression - Type inference tools."""

from codebax_mcp.mcp_server.models.input import GetExpectedAtPositionInput, InferExpressionInput
from codebax_mcp.mcp_server.models.output import GetExpectedAtPositionOutput, InferExpressionOutput


def get_expected_at_position(input: GetExpectedAtPositionInput) -> GetExpectedAtPositionOutput:
    """Get expected type at a specific code position."""
    return GetExpectedAtPositionOutput(
        file=input.file,
        line=input.line,
        column=input.column,
        expected_type=None,
        possible_values=[],
        context=None,
        notes="Type inference requires Pyright LSP integration (Phase 6)",
    )


def infer_expression(input: InferExpressionInput) -> InferExpressionOutput:
    """Infer type of an expression."""
    return InferExpressionOutput(
        expression=input.expression,
        inferred_type=None,
        confidence=0.0,
        notes="Type inference requires Pyright LSP integration (Phase 6)",
    )
