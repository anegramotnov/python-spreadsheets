from enum import Enum, auto
from typing import List

import graphene as gn
from graphql import ResolveInfo
from starlette.applications import Starlette
from starlette.graphql import GraphQLApp
from starlette.routing import Route


class CellTypes(Enum):
    TEXT = auto()
    NUMBER = auto()
    FORMULA = auto()


CellTypesGraphene = gn.Enum.from_enum(CellTypes)


class CellGrapheneInput(gn.InputObjectType):
    class Meta:
        name = "CellInput"

    row = gn.NonNull(gn.Int)
    column = gn.NonNull(gn.Int)
    value = gn.NonNull(gn.String)


class SpreadsheetGrapheneInput(gn.InputObjectType):
    class Meta:
        name = "SpreadsheetInput"

    cells = gn.NonNull(gn.List(gn.NonNull(CellGrapheneInput)))


class CellGrapheneType(gn.ObjectType):
    class Meta:
        name = "Cell"

    row = gn.NonNull(gn.Int)
    column = gn.NonNull(gn.Int)
    input = gn.NonNull(gn.String)
    output = gn.NonNull(gn.String)
    type = gn.NonNull(CellTypesGraphene)

    @classmethod
    def from_input(cls, cell_input: CellGrapheneInput) -> "CellGrapheneType":
        def get_type(value: str) -> CellTypes:
            if value.isnumeric():
                return CellTypes.NUMBER
            elif value.startswith("lambda"):
                return CellTypes.FORMULA
            else:
                return CellTypes.TEXT

        cell = cls(
            row=cell_input.row,
            column=cell_input.column,
            input=cell_input.value,
            output=cell_input.value,
            type=get_type(str(cell_input.value)),
        )
        return cell


class SpreadsheetGrapheneType(gn.ObjectType):
    class Meta:
        name = "Spreadsheet"

    cells = gn.NonNull(gn.List(gn.NonNull(CellGrapheneType)))


class Query(gn.ObjectType):
    spreadsheet = gn.Field(
        SpreadsheetGrapheneType, spreadsheet=SpreadsheetGrapheneInput(required=True)
    )

    @staticmethod
    def resolve_spreadsheet(
        parent: None, info: ResolveInfo, spreadsheet: SpreadsheetGrapheneInput
    ) -> SpreadsheetGrapheneType:
        output_cells: List[CellGrapheneType] = []
        for cell in spreadsheet.cells:
            output_cells.append(CellGrapheneType.from_input(cell))

        return SpreadsheetGrapheneType(cells=output_cells)


root_schema = gn.Schema(query=Query)

routes = [Route("/graphql", GraphQLApp(schema=root_schema))]

app = Starlette(debug=True, routes=routes)
