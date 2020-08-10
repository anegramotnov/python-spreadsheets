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


class TableGrapheneInput(gn.InputObjectType):
    class Meta:
        name = "TableInput"

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


class TableGrapheneType(gn.ObjectType):
    class Meta:
        name = "Table"

    cells = gn.NonNull(gn.List(gn.NonNull(CellGrapheneType)))


class Query(gn.ObjectType):
    calculate = gn.Field(TableGrapheneType, table=TableGrapheneInput(required=True))

    @staticmethod
    def resolve_calculate(
        parent: None, info: ResolveInfo, table: TableGrapheneInput
    ) -> TableGrapheneType:
        output_cells: List[CellGrapheneType] = []
        for cell in table.cells:
            output_cells.append(CellGrapheneType.from_input(cell))

        return TableGrapheneType(cells=output_cells)


root_schema = gn.Schema(query=Query)

routes = [Route("/graphql", GraphQLApp(schema=root_schema))]

app = Starlette(debug=True, routes=routes)
