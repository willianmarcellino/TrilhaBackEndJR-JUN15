from fastapi import FastAPI

from src.routers import auth, label, user

app = FastAPI()
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(label.router)
