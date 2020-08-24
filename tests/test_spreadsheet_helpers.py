import pytest
from python_spreadsheets.engine.calculation_context import CalculationContext
from python_spreadsheets.engine.formula_calculator import FormulaCalculator
from python_spreadsheets.engine.spreadsheet_helpers import (
    CellHelper,
    ColumnHelper,
    RowHelper,
)
from python_spreadsheets.engine.types import (
    CellIndex,
    FormulaCell,
    NumberCell,
    TextCell,
)

column_number_pairs = (
    ("a", 1),
    ("b", 2),
    ("z", 26),
    ("aa", 27),
    ("az", 52),
    ("xyz", 16900),
)


@pytest.mark.parametrize("column, number", column_number_pairs)
def test_column_helper(column, number):
    column_helper = ColumnHelper(columns_number=100)
    assert number == column_helper.column_to_number(column)
    assert column == column_helper.number_to_column(number)


@pytest.mark.parametrize("column", ("&?", "-a", "123", "xyz"))
def test_incorrect_columns(column):
    column_helper = ColumnHelper(columns_number=100)
    with pytest.raises(ValueError) as _:
        column_helper.validate_column(column)


@pytest.mark.parametrize("number", (0, -1, 101))
def test_incorrect_column_numbers(number):
    column_helper = ColumnHelper(columns_number=100)
    with pytest.raises(ValueError) as _:
        column_helper.validate_number(number)


@pytest.mark.parametrize("row", (0, -1, 101))
def test_row_helper(row):
    row_helper = RowHelper(rows_number=100)
    with pytest.raises(ValueError) as _:
        row_helper.validate_row(row)


cells_types_pairs = (
    ("lambda: 2 + 2", FormulaCell),
    ("lambda: (2 + 2) * 2", FormulaCell),
    ("123", NumberCell),
    (".1", NumberCell),
    ("100.123", NumberCell),
    ("lambda ...", TextCell),
    ("Test", TextCell),
    ("def test():\n  print('test')", TextCell),
)


@pytest.mark.parametrize("input_value, value_type", cells_types_pairs)
def test_type_detection(input_value, value_type):

    cell = CellHelper.create_cell(input_value)

    assert type(cell) == value_type


valid_formula_with_variables = (
    ("lambda: 2 + 2", 4),
    ("lambda: 2 ** 2", 4),
    ("lambda: 2", 2),
    ("lambda: (2 + 4) * 3", 18),
    ("lambda: a1 * 2", 4),
)


@pytest.mark.parametrize("source, expected_result", valid_formula_with_variables)
def test_formula_calculation(source, expected_result):
    calculation_context = CalculationContext()
    calculation_context.add_cell(2.0, cell_index=CellIndex("a", 1))
    result = FormulaCalculator.calculate(
        source=source, calculation_context=calculation_context
    )

    assert result == expected_result


invalid_formulas = (
    "lambda x: x * 2",
    "2 * 2",
    "def test():\n  print('test')",
    "import os",
)


@pytest.mark.parametrize("formula", invalid_formulas)
def test_invalid_formula_detection(formula):
    cell = CellHelper.create_cell(formula)

    assert type(cell) == TextCell
    assert cell.output == cell.input == formula
