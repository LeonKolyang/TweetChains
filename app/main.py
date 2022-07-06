from datetime import datetime
import dotenv
dotenv.load_dotenv()

import uvicorn
from fastapi import FastAPI

from app.core import di
from app.core.logging import logger, setup_logging
from app.routes import api, user_handling, tweets


def init() -> FastAPI:
    start = datetime.utcnow()
    app = FastAPI()
    app.include_router(router=api.router, prefix="/api/v1")
    app.include_router(router=user_handling.router)
    app.include_router(router=tweets.router)
    config = di.get_config()
    setup_logging(config)
    duration = (datetime.utcnow() - start).total_seconds()
    logger.info(
        f"app loaded in [{duration}s]", extra={"duration": duration},
    )
    logger.info(config.__dict__.items())
    return app

app = init()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_config=None)
