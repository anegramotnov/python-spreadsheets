import string
from typing import Optional, Set

from python_spreadsheets.engine.types import (
    Cell,
    CellIndex,
    Deferred,
    FormulaCell,
    NumberCell,
    TextCell,
)

COLUMN_ALPHABET = string.ascii_lowercase


class RowHelper:
    _max_row: int

    def __init__(self, rows_number: int):
        self._max_row = rows_number

    def validate_row(self, row: int) -> None:
        if not (1 <= row < self._max_row):
            raise ValueError(f"Row out of range (1-{self._max_row})")


class ColumnHelper:
    """Набор методов для работы со значениями столбцов."""

    _max_column_number: int
    _allowed_columns: Set[str]

    def __init__(self, columns_number: int):
        self._max_column_number = columns_number

        self._allowed_columns = {
            self.number_to_column(n) for n in range(1, columns_number + 1)
        }

    def validate_column(self, column: str) -> None:
        if not column or not all(c in COLUMN_ALPHABET for c in column):
            raise ValueError(f"Column '{column}' not in valid format ([A-Z]+)")
        if column not in self._allowed_columns:
            max_column = self.number_to_column(self._max_column_number)
            raise ValueError(f"Column out of range (A-{max_column})")

    def validate_number(self, number: int) -> None:
        if not (1 <= number < self._max_column_number):
            raise ValueError(
                f"Column number out of range (1-{self._max_column_number})"
            )

    @staticmethod
    def column_to_number(column: str) -> int:
        result = 0
        for char in column:
            result *= len(COLUMN_ALPHABET)
            result += COLUMN_ALPHABET.index(char) + 1

        return result

    @staticmethod
    def number_to_column(number: int) -> str:

        letters = []
        while number:
            number, reminder = divmod(number - 1, len(COLUMN_ALPHABET))
            letters.append(COLUMN_ALPHABET[reminder])

        result = "".join(reversed(letters))

        return result


class CellHelper:
    _column_helper: ColumnHelper
    _row_helper: RowHelper

    def __init__(self, columns_number: int, rows_number: int):
        self._column_helper = ColumnHelper(columns_number=columns_number)
        self._row_helper = RowHelper(rows_number=rows_number)

    def create_cell_index(self, column: str, row: int) -> CellIndex:
        """Создание и валидация объекта индекса ячейки.

        Args:
            column: символьное представление столбца
            row: числовое представление строки

        Returns: Провалидированный объект индекса ячейки
        Raises:
            ValueError: при выходе за границы возможных значений и некорректных
                        значениях
        """
        self._column_helper.validate_column(column)
        self._row_helper.validate_row(row)

        return CellIndex(column=column, row=row)

    @staticmethod
    def to_float_or_none(value: str) -> Optional[float]:
        try:
            number = float(value)
            return number
        except ValueError:
            return None

    @staticmethod
    def is_formula(value: str) -> bool:
        return True if value.startswith("lambda:") else False

    @classmethod
    def create_cell(cls, value: str) -> Cell:
        """Создание объекта ячейки.

        Args:
            value: строковое содержимое ячейки

        Returns: Объект ячейки соответствующего содержимому типа
        """
        number = cls.to_float_or_none(value)
        if number:
            return NumberCell(input=value, output=str(number), value=number)

        if cls.is_formula(value):
            return FormulaCell(
                input=value,
                output=Deferred(),
                value=Deferred(),
                function=Deferred(),
                dependencies=Deferred(),
            )

        return TextCell(input=value, output=value)
