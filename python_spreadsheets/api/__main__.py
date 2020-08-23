import sys

import uvicorn

sys.argv.insert(1, "python_spreadsheets.api.application:app")
uvicorn.main()
