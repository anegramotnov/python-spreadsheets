"""Объекты для использования в коде формул."""

from typing import AbstractSet, Any, Dict, List, SupportsFloat

from python_spreadsheets.engine.spreadsheet_helpers import ColumnHelper
from python_spreadsheets.engine.types import CellIndex


class CellVariable(float):
    index: CellIndex

    def __new__(cls, value: SupportsFloat, index: CellIndex) -> "CellVariable":
        return super().__new__(cls, value)  # type: ignore[call-arg]  # mypy bug

    def __init__(self, value: SupportsFloat, index: CellIndex):
        self.index = index


class CellSlicer:
    """Объект, позволяющий извлекать диапазоны ячеек."""

    _cells: Dict[CellIndex, CellVariable]

    def __init__(self) -> None:
        self._cells = {}

    def add_cell(self, cell: CellVariable) -> None:
        self._cells[cell.index] = cell

    @staticmethod
    def _check_slice_types(value: slice) -> None:
        if not isinstance(value.start, CellVariable):
            raise ValueError(f"Start in {value} must be a CellVariable")
        if not isinstance(value.stop, CellVariable):
            raise ValueError(f"Stop in {value} must be CellVariable")
        if value.step:
            raise ValueError("Step is not supported")

    def get_cells(self, cell_slice: slice) -> List[CellVariable]:
        start_column_number = ColumnHelper.column_to_number(
            cell_slice.start.index.column
        )
        start_row = cell_slice.start.index.row

        stop_column_number = ColumnHelper.column_to_number(cell_slice.stop.index.column)
        stop_row = cell_slice.stop.index.row

        result = []
        for column_number in range(start_column_number, stop_column_number + 1):
            for row in range(start_row, stop_row + 1):
                cell_index = CellIndex(
                    column=ColumnHelper.number_to_column(column_number), row=row,
                )
                result.append(self._cells[cell_index])

        return result

    def __getitem__(self, item: slice) -> List[CellVariable]:
        if isinstance(item, slice):
            self._check_slice_types(item)
            return self.get_cells(cell_slice=item)
        else:
            raise ValueError(f"CellSlicer indices must be slice, not {type(item)}")


class CalculationContext:
    _context: Dict[str, Any]

    _slicer: CellSlicer

    _builtin_functions = {"sum": sum, "min": min, "max": max}

    def __init__(self) -> None:
        self._context = {}

        self._slicer = CellSlicer()
        self._context["s"] = self._slicer
        self._context.update(self._builtin_functions)

    def add_cell(self, value: float, cell_index: CellIndex) -> None:
        cell = CellVariable(value, index=cell_index)
        self._slicer.add_cell(cell)
        self._context[cell_index.as_string()] = cell

    @property
    def context(self) -> Dict[str, Any]:
        return self._context

    @property
    def names(self) -> AbstractSet[str]:
        return self._context.keys()
