from contextlib import asynccontextmanager
from typing import AsyncIterator

import httpx
from fastapi import FastAPI

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
    import logging
    import json

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
    app.include_router(public_router)
    app.include_router(internal_router)
    return app
