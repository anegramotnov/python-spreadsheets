import graphene as gn
from graphql import GraphQLError, ResolveInfo
from python_spreadsheets.api.graphene_types import (
    CellGrapheneType,
    SpreadsheetGrapheneInput,
    SpreadsheetGrapheneType,
)
from python_spreadsheets.engine.spreadsheet_calculator import SpreadsheetCalculator
from starlette.applications import Starlette
from starlette.graphql import GraphQLApp
from starlette.routing import Route

DEFAULT_ROW_COUNT = 100
DEFAULT_COLUMN_COUNT = 26


class CalculateSpreadsheet(gn.Mutation):
    class Arguments:
        input_spreadsheet = SpreadsheetGrapheneInput()

    Output = SpreadsheetGrapheneType

    @staticmethod
    def mutate(
        root: None, info: ResolveInfo, input_spreadsheet: SpreadsheetGrapheneInput
    ) -> "SpreadsheetGrapheneType":

        spreadsheet = SpreadsheetCalculator(
            columns_number=DEFAULT_COLUMN_COUNT, rows_number=DEFAULT_ROW_COUNT
        )

        for cell_index, cell in enumerate(input_spreadsheet.cells):
            try:
                spreadsheet.add_cell(column=cell.column, row=cell.row, value=cell.value)
            except ValueError as e:
                raise GraphQLError(
                    message=f"Error while adding cell #{cell_index}: {e}",
                )

        spreadsheet.calculate()

        calculated_cells = (
            CellGrapheneType(
                column=cell_index.column,
                row=cell_index.row,
                input=cell.input,
                output=cell.output,
            )
            for cell_index, cell in spreadsheet.cells.items()
        )

        return SpreadsheetGrapheneType(cells=calculated_cells)


class SpreadsheetMutations(gn.ObjectType):
    calculate_spreadsheet = CalculateSpreadsheet.Field()


root_schema = gn.Schema(mutation=SpreadsheetMutations)

routes = [Route("/graphql", GraphQLApp(schema=root_schema))]

app = Starlette(debug=True, routes=routes)
