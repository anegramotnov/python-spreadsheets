from enum import Enum, auto
from string import ascii_uppercase
from typing import Dict, Iterator, List, NamedTuple, Set


class CellTypes(Enum):
    TEXT = auto()
    NUMBER = auto()
    FORMULA = auto()


class Cell(NamedTuple):
    row: int
    column: str
    type: CellTypes
    input: str


class CalculatedCell(NamedTuple):
    row: int
    column: str
    type: CellTypes
    input: str
    output: str


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
        if not column or not all(c in ascii_uppercase for c in column):
            raise ValueError(f"Column '{column}' not in valid format ([A-Z]+)")
        if column not in self._allowed_columns:
            max_column = self.get_column_by_number(self._max_column_number)
            raise ValueError(f"Column out of range (A-{max_column})")

    def validate_number(self, number: int) -> None:
        if not 1 <= number < self._max_column_number:
            raise ValueError(
                f"Column number out of range (1-{self._max_column_number})"
            )

    def get_number_by_column(self, column: str) -> int:
        result = 0
        for char in column:
            result *= len(ascii_uppercase)
            result += ascii_uppercase.index(char) + 1

        return result

    def get_column_by_number(self, number: int) -> str:

        letters = []
        while number:
            number, reminder = divmod(number - 1, len(ascii_uppercase))
            letters.append(ascii_uppercase[reminder])

        result = "".join(reversed(letters))

        return result


class CellHelper:
    @staticmethod
    def is_float(value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False

    @classmethod
    def get_type(cls, value: str) -> CellTypes:
        if cls.is_float(value):
            return CellTypes.NUMBER
        elif value.startswith("lambda"):
            return CellTypes.FORMULA
        else:
            return CellTypes.TEXT


class Spreadsheet:
    _cells_map: Dict[int, Dict[str, Cell]]
    _formula_cells: List[Cell]

    _calculated_cells: List[CalculatedCell]

    _row_helper: RowHelper
    _column_helper: ColumnHelper
    _cell_type_helper: CellHelper

    def __init__(self, rows: int, columns: int):
        self._row_helper = RowHelper(rows=rows)
        self._column_helper = ColumnHelper(columns=columns)
        self._cell_helper = CellHelper()

        self._cells_map = {}
        self._formula_cells = []
        self._calculated_cells = []

    def _get_cell(self, row: int, column: str, value: str) -> Cell:

        self._column_helper.validate_column(column=column)
        self._row_helper.validate_row(row=row)

        cell_type = self._cell_helper.get_type(value=value)

        return Cell(row=row, column=column, input=value, type=cell_type)

    def add_cell(self, row: int, column: str, value: str) -> None:
        cell = self._get_cell(row=row, column=column, value=value)

        if row not in self._cells_map:
            self._cells_map[row] = {}
        if column in self._cells_map[row]:
            raise ValueError(f"Cell {column}{row} already exists")
        else:
            self._cells_map[row][column] = cell

        if cell.type == CellTypes.FORMULA:
            self._formula_cells.append(cell)

    @property
    def cells(self) -> Iterator[Cell]:
        for _, row in self._cells_map.items():
            for _, cell in row.items():
                yield cell

    @property
    def calculated_cells(self) -> Iterator[CalculatedCell]:
        for cell in self._calculated_cells:
            yield cell

    def calculate(self) -> None:
        for cell in self.cells:
            calculated_cell = CalculatedCell(  # type: ignore[misc]
                **cell._asdict(), output=cell.input
            )
            self._calculated_cells.append(calculated_cell)
