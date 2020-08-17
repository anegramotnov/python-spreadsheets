import pytest
from spreadsheet_engine.calculator import (
    CellHelper,
    ColumnHelper,
    FormulaValue,
    InputCell,
    NumberValue,
)

column_number_pairs = (
    ("A", 1),
    ("B", 2),
    ("Z", 26),
    ("AA", 27),
    ("AZ", 52),
    ("XYZ", 16900),
)


@pytest.mark.parametrize("column, number", column_number_pairs)
def test_column_helper(column, number):
    column_helper = ColumnHelper(columns=100)
    assert number == column_helper.get_number_by_column(column)
    assert column == column_helper.get_column_by_number(number)


@pytest.mark.parametrize("column", ("&?", "-A", "123"))
def test_incorrect_columns(column):
    column_helper = ColumnHelper(columns=100)
    with pytest.raises(ValueError) as _:
        column_helper.validate_column(column)


@pytest.mark.parametrize("number", (0, -1, 101))
def test_incorrect_column_numbers(number):
    column_helper = ColumnHelper(columns=100)
    with pytest.raises(ValueError) as _:
        column_helper.validate_number(number)


cells_types_pairs = (
    ("lambda: 2 + 2", FormulaValue),
    ("lambda: (2 + 2) * 2", FormulaValue),
    ("123", NumberValue),
    (".1", NumberValue),
    ("100.123", NumberValue),
    ("lambda ...", type(None)),
    ("Test", type(None)),
    ("def test():\n  print('test')", type(None)),
)


@pytest.mark.parametrize("input_value, value_type", cells_types_pairs)
def test_type_detection(input_value, value_type):
    input_cell = InputCell(column="A", row=1, input=input_value)
    calculated_cell = CellHelper.get_calculated_cell(input_cell)
    assert type(calculated_cell.value) == value_type
