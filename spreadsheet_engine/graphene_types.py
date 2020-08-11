import graphene as gn
from spreadsheet_engine.calculator import CellTypes

CellTypesGraphene = gn.Enum.from_enum(CellTypes)


class CellGrapheneInput(gn.InputObjectType):
    class Meta:
        name = "CellInput"

    row = gn.NonNull(gn.Int)
    column = gn.NonNull(gn.String)
    value = gn.NonNull(gn.String)


class SpreadsheetGrapheneInput(gn.InputObjectType):
    class Meta:
        name = "SpreadsheetInput"

    cells = gn.NonNull(gn.List(gn.NonNull(CellGrapheneInput)))


class CellGrapheneType(gn.ObjectType):
    class Meta:
        name = "Cell"

    row = gn.NonNull(gn.Int)
    column = gn.NonNull(gn.String)
    input = gn.NonNull(gn.String)
    output = gn.NonNull(gn.String)
    type = gn.NonNull(CellTypesGraphene)


class SpreadsheetGrapheneType(gn.ObjectType):
    class Meta:
        name = "Spreadsheet"

    cells = gn.NonNull(gn.List(gn.NonNull(CellGrapheneType)))
