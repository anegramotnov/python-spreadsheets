import csv
from pathlib import Path
from typing import Iterator, Tuple

from python_spreadsheets.engine.spreadsheet_calculator import SpreadsheetCalculator
from python_spreadsheets.engine.spreadsheet_helpers import ColumnHelper
from python_spreadsheets.engine.types import Cell, CellIndex, Deferred


def _tsv_to_cells(tsv_path: Path) -> Iterator[Tuple[CellIndex, Cell]]:
    with open(tsv_path, "r", newline="") as tsv_file:
        tsv_reader = csv.reader(tsv_file, delimiter="\t")
        next(tsv_reader)  # skip first row

        for row_index, row in enumerate(tsv_reader, start=1):
            for column_index, cell_input in enumerate(
                row[1:], start=1
            ):  # skip first column
                cell_index = CellIndex(
                    column=ColumnHelper.number_to_column(column_index), row=row_index
                )
                cell = Cell(input=cell_input, output=Deferred())
                yield (cell_index, cell)


def load_from_tsv(tsv_path: Path) -> SpreadsheetCalculator:
    cells_with_index = _tsv_to_cells(tsv_path)

    spreadsheet_calculator = SpreadsheetCalculator(
        columns_number=1000, rows_number=1000
    )

    for cell_index, cell in cells_with_index:
        spreadsheet_calculator.add_cell(
            column=cell_index.column, row=cell_index.row, value=cell.input
        )

    return spreadsheet_calculator
