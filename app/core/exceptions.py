from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import ORJSONResponse
from app.helpers.response_envelope import error_response
from app.core.config import get_settings
from app.core.logger import logger
import traceback

settings = get_settings()

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(f"HTTP {exc.status_code} error: {exc.detail} - Path: {request.url.path}")
        body = error_response(
            request,
            status_code=exc.status_code,
            message=str(exc.detail) if exc.detail is not None else "HTTP error",
            error={"type": "HTTPException"}
        )
        return ORJSONResponse(status_code=exc.status_code, content=body)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
        
        error_detail = {"type": exc.__class__.__name__}
        if settings.DEBUG:
            error_detail["detail"] = str(exc)
            error_detail["traceback"] = traceback.format_exc()
        
        body = error_response(
            request,
            status_code=500,
            message="Internal server error" if not settings.DEBUG else str(exc),
            error=error_detail
        )
        return ORJSONResponse(status_code=500, content=body)
