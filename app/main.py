from fastapi import FastAPI
from app.presentation.api.main import router

app: FastAPI = FastAPI()
app.include_router(router)
