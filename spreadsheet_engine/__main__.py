import sys

import uvicorn

sys.argv.insert(1, "spreadsheet_engine.main:app")
uvicorn.main()
