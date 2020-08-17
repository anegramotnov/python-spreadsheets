import ast
import string
from typing import Callable, Dict, Iterator, List, NamedTuple, Optional, Set, Union

COLUMN_ALPHABET = string.ascii_uppercase


class InputCell(NamedTuple):
    column: str
    row: int
    input: str


class NumberValue(NamedTuple):
    value: float


class FormulaValue(NamedTuple):
    value: float


class CalculatedCell(NamedTuple):
    column: str
    row: int
    input: str
    output: str
    value: Union[None, NumberValue, FormulaValue] = None


class RowHelper:
    _max_row: int

    def __init__(self, rows: int):
        self._max_row = rows

    def validate_row(self, row: int) -> None:
        if not (1 <= row < self._max_row):
            raise ValueError(f"Row out of range (1-{self._max_row})")


class ColumnHelper:
    _max_column_number: int
    _allowed_columns: Set[str]

    def __init__(self, columns: int):
        self._max_column_number = columns

        self._allowed_columns = {
            self.get_column_by_number(n) for n in range(1, columns + 1)
        }

    def validate_column(self, column: str) -> None:
        if not column or not all(c in COLUMN_ALPHABET for c in column):
            raise ValueError(f"Column '{column}' not in valid format ([A-Z]+)")
        if column not in self._allowed_columns:
            max_column = self.get_column_by_number(self._max_column_number)
            raise ValueError(f"Column out of range (A-{max_column})")

    def validate_number(self, number: int) -> None:
        if not (1 <= number < self._max_column_number):
            raise ValueError(
                f"Column number out of range (1-{self._max_column_number})"
            )

    def get_number_by_column(self, column: str) -> int:
        result = 0
        for char in column:
            result *= len(COLUMN_ALPHABET)
            result += COLUMN_ALPHABET.index(char) + 1

        return result

    def get_column_by_number(self, number: int) -> str:

        letters = []
        while number:
            number, reminder = divmod(number - 1, len(COLUMN_ALPHABET))
            letters.append(COLUMN_ALPHABET[reminder])

        result = "".join(reversed(letters))

        return result


class FormulaHelper:
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

    _allowed_body_roots = _allowed_literals | _allowed_expressions

    _allowed_body_nodes = (
        _allowed_literals
        | _allowed_expressions
        | _bin_operators
        | _unary_operators
        | _compare_operators
        | _allowed_literals
    )

    @classmethod
    def validate(cls, source: str) -> None:
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


class CellHelper:
    _formula_helper = FormulaHelper

    @staticmethod
    def get_float_or_none(value: str) -> Optional[float]:
        try:
            number = float(value)
            return number
        except ValueError:
            return None

    @classmethod
    def get_callable_or_none(cls, value: str) -> Optional[Callable]:
        try:
            cls._formula_helper.validate(value)
        except (ValueError, SyntaxError):
            return None

        formula = eval(value, {}, {})
        return formula

    @classmethod
    def get_calculated_cell(cls, cell: InputCell) -> CalculatedCell:

        number = cls.get_float_or_none(cell.input)
        if number:
            return CalculatedCell(  # type: ignore[misc]
                **cell._asdict(), output=cell.input, value=NumberValue(number)
            )

        formula = cls.get_callable_or_none(cell.input)
        if formula:
            result = formula()
            return CalculatedCell(  # type: ignore[misc]
                **cell._asdict(), output=str(result), value=FormulaValue(result)
            )

        return CalculatedCell(**cell._asdict(), output=cell.input)  # type: ignore[misc]


class Spreadsheet:
    _cells_map: Dict[int, Dict[str, InputCell]]
    _formula_cells: List[InputCell]

    _calculated_cells: List[CalculatedCell]

    _column_helper: ColumnHelper
    _row_helper: RowHelper

    _cell_helper: CellHelper

    def __init__(self, columns: int, rows: int):
        self._column_helper = ColumnHelper(columns=columns)
        self._row_helper = RowHelper(rows=rows)

        self._cell_helper = CellHelper()

        self._cells_map = {}
        self._formula_cells = []
        self._calculated_cells = []

    def _get_cell(self, row: int, column: str, value: str) -> InputCell:  # TODO: rename

        self._column_helper.validate_column(column=column)
        self._row_helper.validate_row(row=row)

        return InputCell(row=row, column=column, input=value)

    def add_cell(self, column: str, row: int, value: str) -> None:

        cell = self._get_cell(row=row, column=column, value=value)

        if row not in self._cells_map:
            self._cells_map[row] = {}
        if column in self._cells_map[row]:
            raise ValueError(f"Cell {column}{row} already exists")
        else:
            self._cells_map[row][column] = cell

    @property
    def cells(self) -> Iterator[InputCell]:
        for _, row in self._cells_map.items():
            for _, cell in row.items():
                yield cell

    @property
    def calculated_cells(self) -> Iterator[CalculatedCell]:
        for cell in self._calculated_cells:
            yield cell

    def calculate(self) -> None:
        for cell in self.cells:
            calculated_cell = self._cell_helper.get_calculated_cell(cell)
            self._calculated_cells.append(calculated_cell)
