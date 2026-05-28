"""Application entrypoint for running the FastAPI server.

DESCRIPTION
Starts an Uvicorn server hosting the FastAPI application defined in
`infrastructure.api.app` when executed as a script.

EXAMPLES
Run locally:
    python main.py
"""

import uvicorn

if __name__ == "__main__":
    """Start the Uvicorn development server.

    ARGS
    None

    RETURN
    None

    EXAMPLES
    >>> python main.py
    """
    uvicorn.run("infrastructure.api.app:app", host="127.0.0.1", port=8080, reload=True)
