from typing import Dict, Iterator, List, Optional

from python_spreadsheets.engine.calculation_context import CalculationContext
from python_spreadsheets.engine.formula_calculator import FormulaCalculator
from python_spreadsheets.engine.spreadsheet_helpers import CellHelper
from python_spreadsheets.engine.types import (
    Cell,
    CellIndex,
    CellWithIndex,
    ErrorValue,
    FormulaCell,
    NumberCell,
)


class SpreadsheetCalculator:
    _cell_helper: CellHelper
    _formula_helper: FormulaCalculator

    _cells_map: Dict[CellIndex, Cell]
    _formula_cells: List[CellIndex]
    _calculation_context: CalculationContext

    def __init__(self, columns_number: int, rows_number: int):
        self._cell_helper = CellHelper(
            columns_number=columns_number, rows_number=rows_number
        )
        self._formula_helper = FormulaCalculator()

        self._cells_map = {}
        self._formula_cells = []
        self._calculation_context = CalculationContext()

    def add_cell(self, column: str, row: int, value: str) -> None:

        cell_index = self._cell_helper.create_cell_index(column=column, row=row)

        cell = self._cell_helper.create_cell(value)

        if cell_index in self._cells_map:
            raise ValueError(f"Cell {column}{row} already exists")
        else:
            self._cells_map[cell_index] = cell
            if isinstance(cell, FormulaCell):
                self._formula_cells.append(cell_index)
            if isinstance(cell, NumberCell):
                self._calculation_context.add_cell(
                    value=cell.value, cell_index=cell_index
                )

    @property
    def cells(self) -> Iterator[CellWithIndex]:
        for cell_index, cell in self._cells_map.items():
            yield CellWithIndex(cell_index, cell)

    def get_cell(self, column: str, row: int) -> Optional[Cell]:
        cell = self._cells_map.get(CellIndex(column, row))
        return cell

    def calculate(self) -> None:
        for formula_index in self._formula_cells:
            formula = self._cells_map[formula_index]
            if isinstance(formula, FormulaCell):
                try:
                    formula.value = self._formula_helper.calculate(
                        source=formula.input,
                        calculation_context=self._calculation_context,
                    )
                    formula.output = str(formula.value)
                except Exception as e:
                    formula.value = ErrorValue()
                    formula.output = str(e)
