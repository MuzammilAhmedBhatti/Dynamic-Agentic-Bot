from __future__ import annotations

import math
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
]


@dataclass(frozen=True, slots=True)
class CalculationRequest:
    operation: MathOperation
    values: list[float]
    unit: str | None = None


@dataclass(frozen=True, slots=True)
class CalculationResult:
    operation: str
    inputs: list[float]
    result: float
    unit: str | None = None


class MathService:
    def calculate(self, request: CalculationRequest) -> CalculationResult:
        values = request.values
        if not values or len(values) > 100 or not all(math.isfinite(value) for value in values):
            raise AppError(
                status_code=422,
                code="INVALID_CALCULATION",
                message="The calculation inputs are invalid.",
            )
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

    @staticmethod
    def _nonzero(value: float) -> None:
        if value == 0:
            raise AppError(
                status_code=422, code="DIVISION_BY_ZERO", message="Division by zero is not allowed."
            )
