from __future__ import annotations

import re
from dataclasses import dataclass
from typing import cast

from sqlglot import exp, parse
from sqlglot.errors import ParseError

from dynamic_agentic_api.errors import AppError

_IDENTIFIER = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
_FORBIDDEN_NODES = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Create,
    exp.Alter,
    exp.Command,
    exp.Copy,
    exp.Merge,
    exp.Grant,
    exp.Revoke,
)
_SAFE_FUNCTIONS = frozenset(
    {
        "avg",
        "count",
        "sum",
        "min",
        "max",
        "round",
        "coalesce",
        "nullif",
        "date_trunc",
        "extract",
        "lower",
        "upper",
        "length",
        "abs",
        "ceil",
        "floor",
        "cast",
    }
)


@dataclass(frozen=True, slots=True)
class ValidatedSql:
    statement: str
    tables: list[str]


class SqlGuard:
    def __init__(self, *, row_limit: int) -> None:
        self._row_limit = row_limit

    def validate(
        self, statement: str, *, allowed_schema: str, allowed_tables: list[str]
    ) -> ValidatedSql:
        self.validate_identifier(allowed_schema)
        for table in allowed_tables:
            self.validate_identifier(table)
        if "--" in statement or "/*" in statement or "*/" in statement:
            self._reject("SQL comments are not permitted.")
        try:
            expressions = parse(statement, read="postgres")
        except ParseError as exc:
            raise AppError(
                status_code=422, code="UNSAFE_SQL", message="The generated SQL is invalid."
            ) from exc
        if len(expressions) != 1:
            self._reject("Exactly one SQL statement is permitted.")
        root = expressions[0]
        if root is None:
            self._reject("The generated SQL is empty.")
        root = cast(exp.Query, root)
        if not isinstance(root, (exp.Select, exp.Union, exp.Intersect, exp.Except)):
            self._reject("Only read-only SELECT queries are permitted.")
        if any(root.find(node_type) is not None for node_type in _FORBIDDEN_NODES):
            self._reject("Mutation or administrative SQL is prohibited.")
        tables: list[str] = []
        allowed = set(allowed_tables)
        cte_names = {cte.alias_or_name for cte in root.find_all(exp.CTE)}
        for table_expr in root.find_all(exp.Table):
            name = table_expr.name
            schema = table_expr.db
            if not schema and name in cte_names:
                continue
            if name.casefold() in {"pg_catalog", "information_schema"}:
                self._reject("System catalog access is prohibited.")
            if name not in allowed or (schema and schema != allowed_schema):
                self._reject("The query references an unauthorized table or schema.")
            table_expr.set("db", exp.to_identifier(allowed_schema))
            tables.append(name)
        if not tables:
            self._reject("The query must reference an approved table.")
        for function in root.find_all(exp.Func):
            name = function.sql_name().casefold()
            if name not in _SAFE_FUNCTIONS:
                self._reject("The query uses an unauthorized SQL function.")
        if root.args.get("limit") is None:
            root = root.limit(self._row_limit)
        else:
            limit = root.args["limit"].expression
            if not isinstance(limit, exp.Literal) or not limit.is_int:
                self._reject("The row limit must be a fixed integer.")
            if int(limit.this) > self._row_limit:
                root.set("limit", exp.Limit(expression=exp.Literal.number(self._row_limit)))
        return ValidatedSql(root.sql(dialect="postgres"), list(dict.fromkeys(tables)))

    @staticmethod
    def validate_identifier(value: str) -> None:
        if not _IDENTIFIER.fullmatch(value):
            raise AppError(
                status_code=422,
                code="INVALID_IDENTIFIER",
                message="A database identifier is invalid.",
            )

    @staticmethod
    def _reject(message: str) -> None:
        raise AppError(status_code=422, code="UNSAFE_SQL", message=message)
