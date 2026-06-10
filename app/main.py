import logging

from dotenv import load_dotenv
from fastapi import FastAPI

from app.routes import router

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logging.getLogger("strands").setLevel(logging.INFO)

app = FastAPI(title="ReAct Agent API")
app.include_router(router)
