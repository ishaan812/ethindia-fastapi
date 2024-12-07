import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes.workflow_routes import router as workflow_router
import os

load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'), override=True)

os["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os["REPLICATE_API_KEY"] = os.getenv("REPLICATE_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

start_time = time.time()

app.include_router(workflow_router, prefix="/workflow", tags=["Workflow"])


@app.get("/")
def read_root():
    return {"Hello": "World"}
