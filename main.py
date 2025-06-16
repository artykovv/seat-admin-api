from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.routers import routers

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return{
        "message": "Hello world"
    }



app.include_router(routers)