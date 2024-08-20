from fastapi import FastAPI

from src.routers import user

app = FastAPI()
app.include_router(user.router)
