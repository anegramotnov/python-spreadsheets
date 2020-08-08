import graphene
from starlette.applications import Starlette
from starlette.graphql import GraphQLApp
from starlette.routing import Route


class Query(graphene.ObjectType):
    hello = graphene.String()

    @staticmethod
    def resolve_hello(parent, info):
        return "Hello"


root_schema = graphene.Schema(query=Query)

routes = [Route("/graphql", GraphQLApp(schema=root_schema))]

app = Starlette(debug=True, routes=routes)


if __name__ == "__main__":
    import sys

    import uvicorn

    sys.argv.insert(1, "spreadsheet_engine.main:app")
    uvicorn.main()
