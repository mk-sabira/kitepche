from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def add_origin_check(app: FastAPI, allowed_origins: list[str]) -> None:
    @app.middleware("http")
    async def reject_foreign_origins(request: Request, call_next):
        # Browsers send an Origin header on cross-site requests. A request that
        # changes data and comes from an unknown website is refused.
        origin = request.headers.get("origin")
        if (
            request.method not in SAFE_METHODS
            and origin is not None
            and origin not in allowed_origins
        ):
            return JSONResponse(status_code=403, content={"detail": "Origin not allowed"})
        return await call_next(request)
    