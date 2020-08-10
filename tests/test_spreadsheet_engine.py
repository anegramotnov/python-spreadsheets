import pytest
from graphene.test import Client
from spreadsheet_engine.main import root_schema


@pytest.fixture
def client() -> Client:
    return Client(root_schema)


def test_type_detection(client):
    query = """
    query calculate_spreadsheet($spreadsheet: SpreadsheetInput!) {
      spreadsheet(spreadsheet: $spreadsheet) {
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
    variables = {
        "spreadsheet": {
            "cells": [
                {"row": 1, "column": 2, "value": "lolwut"},
                {"row": 1, "column": 2, "value": "12"},
                {"row": 1, "column": 2, "value": "lambda: 12"},
            ]
        }
    }
    result = client.execute(query, variable_values=variables)

    assert "errors" not in result

    assert result == {
        "data": {
            "spreadsheet": {
                "cells": [
                    {
                        "row": 1,
                        "column": 2,
                        "input": "lolwut",
                        "output": "lolwut",
                        "type": "TEXT",
                    },
                    {
                        "row": 1,
                        "column": 2,
                        "input": "12",
                        "output": "12",
                        "type": "NUMBER",
                    },
                    {
                        "row": 1,
                        "column": 2,
                        "input": "lambda: 12",
                        "output": "lambda: 12",
                        "type": "FORMULA",
                    },
                ]
            }
        }
    }
