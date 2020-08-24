import pytest
from python_spreadsheets.engine.calculation_context import CalculationContext
from python_spreadsheets.engine.formula_calculator import (
    FormulaCalculator,
    FormulaRuntimeError,
)


@pytest.mark.parametrize(
    "source",
    (
        "lambda x: x * 2",
        "2 * 2",
        "def test():\n  print('test')",
        "lambda: __import__('os')",
        "lambda: True; lambda: True",
        "import os",
        "lambda: []",
        "lambda: test(lambda: None)",
    ),
)
def test_formula_validation_error(source):

    with pytest.raises(ValueError):
        FormulaCalculator.validate(source=source, allowed_names={"test"})


def test_formula_runtime_error():
    with pytest.raises(FormulaRuntimeError):
        FormulaCalculator.calculate(
            source="lambda: None", calculation_context=CalculationContext()
        )
