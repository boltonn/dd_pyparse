import uvicorn
from fastapi import FastAPI, File, Query, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from pyparse.schemas.settings import Settings
from pyparse.utils.exceptions import python_exception_handler, validation_exception_handler
from pyparse.utils.logging import make_logger

settings = Settings()
# logger = make_logger(level=settings.log_level, file_path=settings.log_file)
from loguru import logger

app = FastAPI(
    title="Pyparse",
    description="Pyparse",
    version="0.0.1"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"])

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, python_exception_handler)

# @app.get("/")
# async def docs_redirect():
#     return RedirectResponse("/docs")

@app.post("/run")
async def run(
    file: UploadFile = File(...),
    encoding: str = Query(None),
    extract_children: bool = Query(False)
):
    import os
    logger.info(os.listdir("/data"))
    os.makedirs("/data/test", exist_ok=True)
    return "test"


def main():
    uvicorn.run("pyparse.api:app", host=settings.host, port=settings.port, reload=settings.reload)

if __name__ == "__main__":
    main()
    
