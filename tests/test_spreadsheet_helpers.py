import pytest
from spreadsheet_engine.calculator import CellHelper, CellTypes, ColumnHelper

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
    ("lambda ...", CellTypes.FORMULA),
    ("123", CellTypes.NUMBER),
    (".1", CellTypes.NUMBER),
    ("100.123", CellTypes.NUMBER),
    ("Test", CellTypes.TEXT),
    ("def test():\n  print('test')", CellTypes.TEXT),
)


@pytest.mark.parametrize("cell, cell_type", cells_types_pairs)
def test_type_detection(cell, cell_type):
    assert CellHelper.get_type(cell) == cell_type
