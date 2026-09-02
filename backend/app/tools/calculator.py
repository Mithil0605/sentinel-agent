from __future__ import annotations

import ast
import operator as op

from .registry import ToolDefinition

ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.Mod: op.mod,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Unsupported literal")
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return ALLOWED_OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
        return ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.operand))
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    raise ValueError("Expression contains unsupported operations")


def calculate(expression: str):
    tree = ast.parse(expression, mode="eval")
    result = _safe_eval(tree.body)
    if isinstance(result, float):
        result = round(result, 6)
    return {"expression": expression, "result": result, "success": True}


def definition() -> ToolDefinition:
    return ToolDefinition(
        name="calculator",
        description=(
            "Evaluate a safe arithmetic expression (+, -, *, /, **, %). "
            "Use for any math or calculation request."
        ),
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Arithmetic expression to evaluate, e.g. '2 + 3 * 4'",
                }
            },
            "required": ["expression"],
        },
        handler=calculate,
    )
