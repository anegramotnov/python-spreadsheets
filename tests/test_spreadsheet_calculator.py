from pathlib import Path

import pytest
from python_spreadsheets.engine.loaders import _tsv_to_cells, load_from_tsv
from python_spreadsheets.engine.spreadsheet_calculator import SpreadsheetCalculator
from python_spreadsheets.engine.types import ErrorValue


@pytest.fixture
def spreadsheet_calculator():
    spreadsheet_calculator = SpreadsheetCalculator(columns_number=26, rows_number=100)
    return spreadsheet_calculator


def test_simple_formula(spreadsheet_calculator):
    spreadsheet_calculator.add_cell(column="a", row=1, value="lambda: 2 + 2")

    spreadsheet_calculator.calculate()

    cell = spreadsheet_calculator.get_cell("a", 1)

    assert cell.value == 4
    assert cell.output == "4.0"


def test_related_formula(spreadsheet_calculator):
    spreadsheet_calculator.add_cell(column="a", row=1, value="2")
    spreadsheet_calculator.add_cell(column="a", row=2, value="lambda: a1 * 2")

    spreadsheet_calculator.calculate()

    cell = spreadsheet_calculator.get_cell("a", 2)

    assert cell.value == 4
    assert cell.output == "4.0"


def test_slice_formula(spreadsheet_calculator):
    spreadsheet_calculator.add_cell(column="a", row=1, value="2")
    spreadsheet_calculator.add_cell(column="a", row=2, value="2")
    spreadsheet_calculator.add_cell(column="a", row=3, value="2")
    spreadsheet_calculator.add_cell(column="a", row=4, value="lambda: sum(s[a1:a3])")

    spreadsheet_calculator.calculate()

    cell = spreadsheet_calculator.get_cell("a", 4)

    assert cell.value == 6
    assert cell.output == "6.0"


def test_runtime_error_in_formula(spreadsheet_calculator):
    spreadsheet_calculator.add_cell(column="a", row=1, value="2")
    spreadsheet_calculator.add_cell(column="a", row=2, value="lambda: sum(a1)")

    spreadsheet_calculator.calculate()

    cell = spreadsheet_calculator.get_cell("a", 2)

    assert type(cell.value) == ErrorValue


def spreadsheets_from_tsv():
    spreadsheet_cases_path = Path(__file__).parent / "spreadsheet_cases"
    for spreadsheet_case in spreadsheet_cases_path.iterdir():
        input_path = spreadsheet_case / "input.tsv"
        output_path = spreadsheet_case / "expected.tsv"

        spreadsheet_calculator = load_from_tsv(input_path)

        output_cells = _tsv_to_cells(output_path)

        yield pytest.param(
            spreadsheet_calculator, output_cells, id=spreadsheet_case.name
        )


@pytest.mark.parametrize(
    "spreadsheet_calculator, expected_cells", spreadsheets_from_tsv()
)
def test_calculation(spreadsheet_calculator, expected_cells):
    spreadsheet_calculator.calculate()

    for expected_cell_index, expected_cell in expected_cells:
        assert spreadsheet_calculator.cells[expected_cell_index]

        calculated_cell = spreadsheet_calculator.cells[expected_cell_index]

        assert calculated_cell.output == expected_cell.input
