import ast
from typing import AbstractSet

from python_spreadsheets.engine.calculation_context import CalculationContext


class FormulaError(Exception):
    pass


class FormulaRuntimeError(FormulaError):
    pass


class FormulaCalculator:
    _allowed_literals = {ast.Num, ast.NameConstant}

    _allowed_expressions = {
        ast.BinOp,
        ast.UnaryOp,
        ast.IfExp,
        ast.Call,
        ast.Compare,
    }

    _bin_operators = {
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
    }

    _unary_operators = {
        ast.UAdd,
        ast.USub,
        ast.Not,
        ast.Invert,
    }

    _bool_operators = {
        ast.And,
        ast.Or,
    }

    _compare_operators = {
        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.LtE,
        ast.Gt,
        ast.GtE,
        ast.Is,
        ast.IsNot,
        ast.In,  # ?
        ast.NotIn,  # ?
    }

    _allowed_name_nodes = {ast.Name, ast.Load}

    _allowed_slice_nodes = {ast.Subscript, ast.Slice}

    _allowed_body_roots = _allowed_literals | _allowed_expressions

    _allowed_body_nodes = (
        _allowed_literals
        | _allowed_expressions
        | _bin_operators
        | _unary_operators
        | _compare_operators
        | _allowed_literals
        | _allowed_name_nodes
        | _allowed_slice_nodes
    )

    _allowed_context_nodes = {ast.Load}

    @classmethod
    def calculate(cls, source: str, calculation_context: CalculationContext) -> float:

        cls.validate(source=source, allowed_names=calculation_context.names)

        global_variables = calculation_context.context

        function = eval(source, global_variables, {})
        try:
            result = function()
        except TypeError as e:
            raise FormulaRuntimeError(f"Runtime error: {e}")

        try:
            return float(result)
        except TypeError:
            raise FormulaRuntimeError(
                f"Formula result must be a number, not {type(result)}"
            )

    @classmethod
    def validate(cls, source: str, allowed_names: AbstractSet[str]) -> None:
        module = ast.parse(source)
        body = module.body

        if len(body) != 1:
            raise ValueError("Source must contain only 1 expression")

        expression = body[0]

        if not isinstance(expression, ast.Expr):
            raise ValueError(f"Source must contain expression but found {expression}")

        lambda_ = expression.value

        if not isinstance(lambda_, ast.Lambda):
            raise ValueError(f"Source must contain lambda but found {lambda_}")

        if lambda_.args.args:
            raise ValueError("Lambda must not contain arguments")

        lambda_body = lambda_.body

        if type(lambda_body) not in cls._allowed_body_roots:
            raise ValueError(
                f"Lambda body must be one of {cls._allowed_body_roots}, "
                f"but found {lambda_body}"
            )

        for node in ast.walk(lambda_body):
            if type(node) not in cls._allowed_body_nodes:
                raise ValueError(f"Found forbidden node in lambda body: {node}")
            if isinstance(node, ast.Name) and node.id not in allowed_names:
                raise ValueError(f"Found forbidden name in lambda body: {node.id}")
