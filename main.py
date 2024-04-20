import os
import uvicorn
import logging
from fastapi import FastAPI
from alembic import command
from alembic.config import Config
from api.routes.routes import routes
from contextlib import asynccontextmanager
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
log = logging.getLogger("uvicorn")

#sincronized migrations
upgrade_database = os.getenv('DATABASE_UPGRADE')
def migrations():
    alembic_config = Config('alembic.ini')
    command.upgrade(alembic_config, 'head')

@asynccontextmanager
async def lifespan(app_: FastAPI):
    if upgrade_database == 'True':
        log.info('Run alembic upgrade head...')
        migrations()
    yield

#cors aplication
origins = [
    '*',
    'http://127.0.0.1:8000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = FastAPI(lifespan= lifespan)
app.include_router(routes)

#openapi config
openapi_schema = get_openapi(
    title='API Credit Card Fraud',
    version='1.1.0',
    summary='Simple api project',
    description='This is OpenAPI schema',
    routes=app.routes
)

app.openapi_schema = openapi_schema

if __name__ == '__main__':
    uvicorn.run('main:app', hostname='127.0.0.1', port=8080)