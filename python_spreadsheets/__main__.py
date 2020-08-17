import sys

import uvicorn

sys.argv.insert(1, "python_spreadsheets.main:app")
uvicorn.main()
