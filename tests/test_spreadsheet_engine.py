import pytest
from graphene.test import Client
from spreadsheet_engine.api import root_schema


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
          type
        }
      }
    }
    """
    variables = {"spreadsheet": {"cells": [{"row": 1, "column": "A", "value": "test"}]}}

    result = client.execute(query, variable_values=variables)

    assert "errors" not in result

    assert result == {
        "data": {
            "calculateSpreadsheet": {
                "cells": [
                    {
                        "row": 1,
                        "column": "A",
                        "input": "test",
                        "output": "test",
                        "type": "TEXT",
                    },
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
                {"row": 1, "column": "A", "value": "test"},
                {"row": 1, "column": "A", "value": "test 2"},
            ]
        }
    }

    result = client.execute(query, variable_values=variables)

    assert (
        result["errors"][0]["message"]
        == "Error while adding cell #1: Cell A1 already exists"
    )
