from dd_pyparse.core.parsers import parse
from dd_pyparse.schemas.settings import Settings
from dd_pyparse.utils.exceptions import (python_exception_handler,
                                         validation_exception_handler)
from dd_pyparse.utils.health import ServiceHealthStatus, service_health
from dd_pyparse.utils.info import ServiceInfo, service_info
from dd_pyparse.utils.logging import logger

try:
    import uvicorn
    from fastapi import FastAPI, File, Query, UploadFile
    from fastapi.exceptions import RequestValidationError
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:
    logger.error("Failed to import uvicorn and/or fastapi. Please install them with `pip install uvicorn fastapi`")
    exit(1)

settings = Settings()

app = FastAPI(title=service_info.title, version=service_info.version, description=service_info.description)

app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, python_exception_handler)


@app.get("/health")
async def health() -> ServiceHealthStatus:
    return service_health.status


@app.get("/info")
async def info() -> ServiceInfo:
    return service_info


@app.post("/infer")
async def infer(
    file: UploadFile = File(...),
    extract_children: bool = Query(False, description="Extract children"),
    **kwargs,
):
    """Infer the file type of a file"""

    return parse(
        file=file.file,
        extract_children=extract_children,
        out_dir=settings.children_dir,
        **kwargs,
    )


def main():
    uvicorn.run("dd_pyparse.interfaces._fastapi:app", host=settings.host, port=settings.port, reload=settings.reload)


if __name__ == "__main__":
    main()
