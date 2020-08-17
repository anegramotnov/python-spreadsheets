import graphene as gn
from graphql import GraphQLError, ResolveInfo
from spreadsheet_engine.calculator import Spreadsheet
from spreadsheet_engine.graphene_types import (
    CellGrapheneType,
    SpreadsheetGrapheneInput,
    SpreadsheetGrapheneType,
)
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

        spreadsheet = Spreadsheet(columns=DEFAULT_COLUMN_COUNT, rows=DEFAULT_ROW_COUNT)

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
                row=cell.row, column=cell.column, input=cell.input, output=cell.output,
            )
            for cell in spreadsheet.calculated_cells
        )

        return SpreadsheetGrapheneType(cells=calculated_cells)


class SpreadsheetMutations(gn.ObjectType):
    calculate_spreadsheet = CalculateSpreadsheet.Field()


root_schema = gn.Schema(mutation=SpreadsheetMutations)

routes = [Route("/graphql", GraphQLApp(schema=root_schema))]

app = Starlette(debug=True, routes=routes)
