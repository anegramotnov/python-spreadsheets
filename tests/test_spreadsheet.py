import pytest
from spreadsheet_engine.calculator import Spreadsheet


@pytest.fixture
def spreadsheet():
    spreadsheet = Spreadsheet(columns=26, rows=100)
    return spreadsheet


def test_simple_formula(spreadsheet):
    spreadsheet.add_cell(column="A", row=1, value="lambda: 2 + 2")

    spreadsheet.calculate()

    calculated_cell = [
        cell
        for cell in spreadsheet.calculated_cells
        if cell.column == "A" and cell.row == 1
    ][0]

    assert calculated_cell.output == "4"
