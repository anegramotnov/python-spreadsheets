import pytest
from graphene.test import Client
from python_spreadsheets.api.application import root_schema


@pytest.fixture
def client() -> Client:
    return Client(root_schema)


def test_calculate_format(client):
    query = """
    mutation calculateSpreadsheet($spreadsheet: SpreadsheetInput!) {
      calculateSpreadsheet(inputSpreadsheet: $spreadsheet) {
        cells {
          row
          column
          input
          output
        }
      }
    }
    """
    variables = {
        "spreadsheet": {
            "cells": [
                {"row": 1, "column": "a", "value": "test"},
                {"row": 2, "column": "b", "value": "lambda: 1"},
            ]
        }
    }

    result = client.execute(query, variable_values=variables)

    assert "errors" not in result

    assert result == {
        "data": {
            "calculateSpreadsheet": {
                "cells": [
                    {"row": 1, "column": "a", "input": "test", "output": "test"},
                    {"row": 2, "column": "b", "input": "lambda: 1", "output": "1.0"},
                ]
            }
        }
    }


def test_cell_duplicate(client):
    query = """
    mutation calculateSpreadsheet($spreadsheet: SpreadsheetInput!) {
      calculateSpreadsheet(inputSpreadsheet: $spreadsheet) {
        cells {
          row
          column
        }
      }
    }
    """
    variables = {
        "spreadsheet": {
            "cells": [
                {"row": 1, "column": "a", "value": "test"},
                {"row": 1, "column": "a", "value": "test 2"},
            ]
        }
    }

    result = client.execute(query, variable_values=variables)

    assert (
        result["errors"][0]["message"]
        == "Error while adding cell #1: Cell a1 already exists"
    )
