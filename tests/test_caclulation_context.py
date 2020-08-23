import pytest
from python_spreadsheets.engine.calculation_context import (
    CalculationContext,
    CellSlicer,
    CellVariable,
)
from python_spreadsheets.engine.types import CellIndex


@pytest.fixture
def cells():
    cells = (
        CellVariable(1.0, CellIndex("a", 1)),
        CellVariable(1.0, CellIndex("a", 2)),
        CellVariable(1.0, CellIndex("a", 3)),
        CellVariable(1.0, CellIndex("b", 1)),
        CellVariable(1.0, CellIndex("b", 2)),
        CellVariable(1.0, CellIndex("b", 3)),
        CellVariable(1.0, CellIndex("c", 1)),
        CellVariable(1.0, CellIndex("c", 2)),
        CellVariable(1.0, CellIndex("c", 3)),
    )
    return cells


@pytest.fixture
def slicer(cells):

    slicer = CellSlicer()

    for cell in cells:
        slicer.add_cell(cell)

    return slicer


def test_vertical_slice(slicer, cells):
    expected_range = [cells[0], cells[1], cells[2]]

    start, stop = expected_range[0], expected_range[-1]

    slice_result = slicer[start:stop]

    assert slice_result == expected_range


def test_horizontal_slice(slicer, cells):
    expected_range = [cells[0], cells[3], cells[6]]

    start, stop = expected_range[0], expected_range[-1]

    slice_result = slicer[start:stop]

    assert slice_result == expected_range


cell_mock = CellVariable(0, CellIndex("a", 1))


@pytest.mark.parametrize(
    "slice_call",
    (
        lambda s: s["start":"stop"],  # type: ignore[misc]
        lambda s: s[1:3],
        lambda s: s[1:cell_mock],  # type: ignore[misc]
        lambda s: s[cell_mock:1],  # type: ignore[misc]
        lambda s: s[0],
        lambda s: s[s],
        lambda s: s[cell_mock:cell_mock:2],  # type: ignore[misc]
    ),
)
def test_slice_errors(slice_call, slicer):
    with pytest.raises(ValueError):
        slice_call(slicer)


def test_calculation_context():
    calculation_context = CalculationContext()

    context_dict = calculation_context.context

    assert context_dict["s"]
    assert type(context_dict["s"]) == CellSlicer

    expected_builtins = ("sum", "min", "max")

    for builtin in expected_builtins:
        assert context_dict[builtin]
        assert callable(context_dict[builtin])
