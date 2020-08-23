from dataclasses import dataclass
from typing import Callable, List, NamedTuple, Union


class Deferred:
    """Значение для еще не посчитанных данных."""

    pass


class CellIndex(NamedTuple):
    column: str
    row: int

    def __str__(self) -> str:
        return f"{self.column}{self.row}"

    def as_string(self) -> str:
        return self.__str__()


class Formula(NamedTuple):
    function: Callable
    dependencies: List[CellIndex]


@dataclass
class Cell:
    input: str
    output: Union[Deferred, str]


class CellWithIndex(NamedTuple):
    cell_index: CellIndex
    cell: Cell


@dataclass
class NumberCell(Cell):
    value: float


@dataclass
class TextCell(Cell):
    pass


class ErrorValue:
    pass


@dataclass
class FormulaCell(Cell):
    value: Union[Deferred, float, ErrorValue]
    function: Union[Deferred, Callable]
    dependencies: Union[Deferred, List[CellIndex]]
