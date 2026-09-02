from __future__ import annotations

import ast
import math
import operator
import re
from collections.abc import Callable
from dataclasses import dataclass
from statistics import fmean
from typing import Literal

from dynamic_agentic_api.errors import AppError

MathOperation = Literal[
    "add",
    "subtract",
    "multiply",
    "divide",
    "percentage",
    "percentage_change",
    "ratio",
    "average",
    "sum",
    "difference",
    "min",
    "max",
    "expression",
]

_MAX_EXPRESSION_LENGTH = 500
_MAX_AST_NODES = 100
_MAX_EXPONENT = 100
_QUESTION_PREFIX = re.compile(
    r"^(?:(?:please\s+)?(?:what\s+is|what's|calculate|compute|evaluate|solve)\s+|"
    r"(?:please\s+)?(?:find|give\s+me)\s+(?:the\s+)?(?:value|result|answer)\s+(?:of|for)\s+)",
    re.IGNORECASE,
)
_BINARY_OPERATORS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
_FUNCTIONS: dict[str, tuple[Callable[..., float], int, int]] = {
    "abs": (abs, 1, 1),
    "ceil": (math.ceil, 1, 1),
    "cos": (math.cos, 1, 1),
    "exp": (math.exp, 1, 1),
    "floor": (math.floor, 1, 1),
    "log": (math.log, 1, 2),
    "log10": (math.log10, 1, 1),
    "max": (max, 1, 20),
    "min": (min, 1, 20),
    "round": (round, 1, 2),
    "sin": (math.sin, 1, 1),
    "sqrt": (math.sqrt, 1, 1),
    "tan": (math.tan, 1, 1),
}
_CONSTANTS = {"e": math.e, "pi": math.pi}


@dataclass(frozen=True, slots=True)
class CalculationRequest:
    operation: MathOperation
    values: list[float]
    unit: str | None = None
    expression: str | None = None


@dataclass(frozen=True, slots=True)
class CalculationResult:
    operation: str
    inputs: list[float]
    result: float
    unit: str | None = None


class MathService:
    def parse_question(self, question: str) -> CalculationRequest | None:
        """Parse a standalone arithmetic question without relying on an LLM."""
        expression = self._normalize_question(question)
        if expression is None:
            return None
        try:
            self._evaluate_expression(expression)
        except AppError:
            return None
        return CalculationRequest("expression", [], expression=expression)

    def calculate(self, request: CalculationRequest) -> CalculationResult:
        values = request.values
        if request.operation == "expression":
            if not request.expression:
                raise self._invalid()
            result, inputs = self._evaluate_expression(request.expression)
            return CalculationResult(request.operation, inputs, round(result, 10), request.unit)
        if not values or len(values) > 100 or not all(math.isfinite(value) for value in values):
            raise self._invalid()
        operation = request.operation
        if (
            operation
            in {"subtract", "divide", "percentage", "percentage_change", "ratio", "difference"}
            and len(values) != 2
        ):
            raise AppError(
                status_code=422,
                code="INVALID_CALCULATION",
                message="This operation requires exactly two values.",
            )
        if operation == "add" or operation == "sum":
            result = sum(values)
        elif operation == "subtract":
            result = values[0] - values[1]
        elif operation == "difference":
            result = abs(values[0] - values[1])
        elif operation == "multiply":
            result = math.prod(values)
        elif operation == "divide" or operation == "ratio":
            self._nonzero(values[1])
            result = values[0] / values[1]
        elif operation == "percentage":
            result = values[0] * values[1] / 100
        elif operation == "percentage_change":
            self._nonzero(values[0])
            result = (values[1] - values[0]) / abs(values[0]) * 100
        elif operation == "average":
            result = fmean(values)
        elif operation == "min":
            result = min(values)
        elif operation == "max":
            result = max(values)
        else:
            raise AppError(
                status_code=422,
                code="INVALID_CALCULATION",
                message="The calculation operation is unsupported.",
            )
        if not math.isfinite(result):
            raise AppError(
                status_code=422,
                code="INVALID_CALCULATION",
                message="The calculation result is not finite.",
            )
        return CalculationResult(operation, list(values), round(result, 10), request.unit)

    @classmethod
    def _normalize_question(cls, question: str) -> str | None:
        candidate = question.strip().rstrip("?.!").strip()
        previous = None
        while candidate != previous:
            previous = candidate
            candidate = _QUESTION_PREFIX.sub("", candidate, count=1).strip()
        candidate = re.sub(
            r"^(?:the\s+)?(?:value|result|answer)\s+of\s+", "", candidate, flags=re.I
        )
        candidate = candidate.replace("\u00d7", "*").replace("\u2715", "*").replace("\u00b7", "*")
        candidate = candidate.replace("\u00f7", "/").replace("\u2212", "-").replace("^", "**")
        candidate = re.sub(r"(?<=\d),(?=\d{3}(?:\D|$))", "", candidate)
        candidate = re.sub(
            r"^multiply\s+(-?\d+(?:\.\d+)?)\s+by\s+(-?\d+(?:\.\d+)?)$",
            r"\1 * \2",
            candidate,
            flags=re.I,
        )
        candidate = re.sub(
            r"^divide\s+(-?\d+(?:\.\d+)?)\s+by\s+(-?\d+(?:\.\d+)?)$",
            r"\1 / \2",
            candidate,
            flags=re.I,
        )
        candidate = re.sub(r"\bmultiplied\s+by\b|\btimes\b", "*", candidate, flags=re.I)
        candidate = re.sub(r"\bdivided\s+by\b", "/", candidate, flags=re.I)
        candidate = re.sub(r"\bto\s+the\s+power\s+of\b", "**", candidate, flags=re.I)
        candidate = re.sub(r"\bplus\b", "+", candidate, flags=re.I)
        candidate = re.sub(r"\bminus\b", "-", candidate, flags=re.I)
        candidate = re.sub(r"(?<=[\d)])\s*[xX]\s*(?=[\d(])", "*", candidate)
        candidate = re.sub(
            r"\b(?:the\s+)?square\s+root\s+of\s+(-?\d+(?:\.\d+)?)\b",
            r"sqrt(\1)",
            candidate,
            flags=re.I,
        )
        candidate = re.sub(
            r"(-?\d+(?:\.\d+)?)\s*(?:%|percent)\s+of\s+(-?\d+(?:\.\d+)?)",
            r"((\1)/100)*(\2)",
            candidate,
            flags=re.I,
        )
        candidate = re.sub(r"(?<=\d)\s*(?=\()", "*", candidate)
        candidate = re.sub(r"(?<=\))\s*(?=[\d(])", "*", candidate)
        candidate = candidate.strip()
        if not candidate or len(candidate) > _MAX_EXPRESSION_LENGTH:
            return None
        if not re.search(r"\d", candidate):
            return None
        if not re.search(
            r"[+*/%()-]|\b(?:sqrt|sin|cos|tan|log|log10|exp|abs|min|max|round|floor|ceil)\b",
            candidate,
            re.I,
        ):
            return None
        if re.search(r"[^\d\s+\-*/%().,A-Za-z_]", candidate):
            return None
        return candidate.casefold()

    @classmethod
    def _evaluate_expression(cls, expression: str) -> tuple[float, list[float]]:
        if not expression or len(expression) > _MAX_EXPRESSION_LENGTH:
            raise cls._invalid()
        try:
            tree = ast.parse(expression, mode="eval")
        except (SyntaxError, ValueError) as exc:
            raise cls._invalid() from exc
        if sum(1 for _ in ast.walk(tree)) > _MAX_AST_NODES:
            raise cls._invalid()
        inputs: list[float] = []

        def evaluate(node: ast.AST) -> float:
            if isinstance(node, ast.Expression):
                return evaluate(node.body)
            if isinstance(node, ast.Constant):
                if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                    raise cls._invalid()
                value = float(node.value)
                if not math.isfinite(value):
                    raise cls._invalid()
                inputs.append(value)
                return value
            if isinstance(node, ast.Name):
                if node.id not in _CONSTANTS:
                    raise cls._invalid()
                return _CONSTANTS[node.id]
            if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
                return _UNARY_OPERATORS[type(node.op)](evaluate(node.operand))
            if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
                left = evaluate(node.left)
                right = evaluate(node.right)
                if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)) and right == 0:
                    raise AppError(
                        status_code=422,
                        code="DIVISION_BY_ZERO",
                        message="Division by zero is not allowed.",
                    )
                if isinstance(node.op, ast.Pow) and abs(right) > _MAX_EXPONENT:
                    raise cls._invalid()
                return float(_BINARY_OPERATORS[type(node.op)](left, right))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                function_spec = _FUNCTIONS.get(node.func.id)
                if function_spec is None or node.keywords:
                    raise cls._invalid()
                function, minimum, maximum = function_spec
                if not minimum <= len(node.args) <= maximum:
                    raise cls._invalid()
                return float(function(*(evaluate(argument) for argument in node.args)))
            raise cls._invalid()

        try:
            result = evaluate(tree)
        except AppError:
            raise
        except (ArithmeticError, OverflowError, ValueError, TypeError) as exc:
            raise cls._invalid() from exc
        if not math.isfinite(result):
            raise cls._invalid()
        return result, inputs

    @staticmethod
    def _invalid() -> AppError:
        return AppError(
            status_code=422,
            code="INVALID_CALCULATION",
            message="The calculation inputs are invalid.",
        )

    @staticmethod
    def _nonzero(value: float) -> None:
        if value == 0:
            raise AppError(
                status_code=422, code="DIVISION_BY_ZERO", message="Division by zero is not allowed."
            )
