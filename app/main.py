#Authentication routes
from app.routes.auth import router as auth_router

from fastapi import FastAPI
from app.routes.predict import router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Supply Chain Risk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

app.include_router(auth_router)