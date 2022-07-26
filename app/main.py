from datetime import datetime
import dotenv

from app.db.db_utils import close_mongo_connection, connect_to_mongo
dotenv.load_dotenv()

import uvicorn
from fastapi import FastAPI, Request, status

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core import di
from app.core.logging import logger, setup_logging
from app.routes import api, tweets, timeslots, users


def init() -> FastAPI:
    start = datetime.utcnow()
    app = FastAPI()

    # bind api routes 
    app.include_router(router=api.router, prefix="/api/v1")
    app.include_router(router=users.router)
    app.include_router(router=tweets.router)
    app.include_router(router=timeslots.router)

    # get config from dependency injection handler
    config = di.get_config()
    setup_logging(config)

    # setup connection and disconnection to mongo
    app.add_event_handler("startup", connect_to_mongo)
    app.add_event_handler("shutdown", close_mongo_connection)

    duration = (datetime.utcnow() - start).total_seconds()
    logger.info(
        f"app loaded in [{duration}s]", extra={"duration": duration},
    )
    logger.info(config.__dict__.items())
    return app


app = init()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logger.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_config=None)
