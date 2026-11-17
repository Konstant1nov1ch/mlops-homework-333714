import os
from contextlib import asynccontextmanager
from pathlib import Path
import joblib
from fastapi import FastAPI
from pydantic import BaseModel, Field

model = None
version = os.getenv('MODEL_VERSION', 'iris-v1')
@asynccontextmanager
async def lifespan(app):
    global model
    model = joblib.load(os.getenv('MODEL_PATH', str(Path(__file__).resolve().parent.parent / 'model.joblib')))
    yield
app = FastAPI(lifespan=lifespan)
class Features(BaseModel):
    features: list[float] = Field(min_length=4, max_length=4)
@app.get('/live')
def live(): return {'status': 'alive'}
@app.get('/health')
def health(): return {'status': 'ready' if model is not None else 'not_ready', 'model_version': version}
@app.post('/predict')
def predict(data: Features): return {'class_id': int(model.predict([data.features])[0]), 'model_version': version}
