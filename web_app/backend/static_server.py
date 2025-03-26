import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import logging

# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize FastAPI application
app = FastAPI(
    title="Intelligent Network Search Static File Server",
    description="Server providing frontend static files",
    version="1.0.0",
)

# Mount the frontend directory
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Provide frontend page"""
    try:
        with open(BASE_DIR / "frontend" / "index.html") as f:
            content = f.read()
        return content
    except Exception as e:
        logging.error(f"Error reading frontend page: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error reading frontend page: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    # Start the uvicorn server
    uvicorn.run(
        "static_server:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
    )
