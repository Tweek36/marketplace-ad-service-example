import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator

import httpx
from fastapi import FastAPI, Request

from src.infrastructure.http.auth_client import AuthServiceUserProfileService
from src.infrastructure.persistence.database import (
    create_engine,
    create_session_factory,
)
from src.presentation.api.dependencies import setup
from src.presentation.api.routes.internal import router as internal_router
from src.presentation.api.routes.public import router as public_router
from src.settings import Settings


def create_app() -> FastAPI:

    # Configure structured logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    logger.info("Starting Ad Service application")

    settings = Settings()

    logger.info("Settings loaded", extra={
        "settings": {
            "auth_service_url": settings.auth_service_url,
            "kafka_bootstrap_servers": settings.kafka_bootstrap_servers,
            "database_url": "***masked***"
        }
    })

    try:
        engine = create_engine(settings)
        session_factory = create_session_factory(engine)
        logger.info("Database engine created successfully")
    except Exception as e:
        logger.error("Failed to create database engine", extra={
            "error": {
                "type": type(e).__name__,
                "message": str(e)
            }
        })
        raise

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        logger.info("Application lifespan startup")
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                user_profile = AuthServiceUserProfileService(
                    client,
                    settings.auth_service_url,
                )
                setup(settings, session_factory, user_profile)
                logger.info("Application setup completed successfully")
                yield
        except Exception as e:
            logger.error("Application lifespan error", extra={
                "error": {
                    "type": type(e).__name__,
                    "message": str(e)
                }
            })
            raise
        finally:
            logger.info("Application lifespan shutdown")

    app = FastAPI(title="Ad Service", lifespan=lifespan)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger = logging.getLogger(__name__)
        start_time = time.time()

        # Log incoming request
        request_body = None
        try:
            if request.method in ["POST", "PUT", "PATCH"]:
                request_body = await request.body()
        except Exception:
            request_body = None

        request_headers = dict(request.headers)
        # Mask sensitive headers
        if "authorization" in request_headers:
            request_headers["authorization"] = "***masked***"
        if "cookie" in request_headers:
            request_headers["cookie"] = "***masked***"

        logger.info(
            "Incoming request",
            extra={
                "http": {
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": str(request.query_params),
                    "status_code": "processing"
                },
                "request": {
                    "headers": request_headers,
                    "size": len(request_body) if request_body else 0,
                    "remote_addr": request.client.host if request.client else None
                }
            }
        )

        try:
            response = await call_next(request)
        except Exception as e:
            # Log exception
            logger.error(
                "Request processing failed",
                extra={
                    "http": {
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": "500",
                        "duration_ms": int((time.time() - start_time) * 1000)
                    },
                    "error": {
                        "type": type(e).__name__,
                        "message": str(e)
                    }
                }
            )
            raise

        # Log response
        duration = int((time.time() - start_time) * 1000)
        response_headers = dict(response.headers)

        logger.info(
            "Request completed",
            extra={
                "http": {
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": str(response.status_code),
                    "duration_ms": duration
                },
                "response": {
                    "headers": response_headers,
                    "size": int(response.headers.get("content-length", 0))
                }
            }
        )

        return response

    app.include_router(public_router)
    app.include_router(internal_router)
    return app
