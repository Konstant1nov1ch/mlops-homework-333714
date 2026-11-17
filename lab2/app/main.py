import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.engine import Engine
engine=None
@asynccontextmanager
async def lifespan(app):
    global engine
    engine=Engine()
    yield
app=FastAPI(lifespan=lifespan)
class Query(BaseModel):
    query:str=Field(min_length=2,max_length=500)
    limit:int=Field(default=3,ge=1,le=10)
@app.get('/live')
def live(): return {'status':'alive'}
@app.get('/ready')
def ready():
    if engine is None: raise HTTPException(503,'index unavailable')
    return {'status':'ready'}
@app.post('/search')
def search(request:Query):
    return {'results':engine.search(request.query,request.limit,os.getenv('RANKING_MODE','normal'))}

@app.get('/meta')
def meta():
    if engine is None: raise HTTPException(503,'index unavailable')
    return {'image_digest':os.getenv('IMAGE_DIGEST','local'),'environment':os.getenv('ENVIRONMENT','local'),'corpus_sha256':engine.corpus_sha256,'ranking_mode':os.getenv('RANKING_MODE','normal')}
