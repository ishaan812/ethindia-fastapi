import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes.workflow_routes import router as workflow_router
from routes.stream_routes import router as stream_router


# Initialize the FastAPI app
app = FastAPI()

# Load environment variables from the .env file
load_dotenv(override=True)
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Start time tracking
start_time = time.time()

# Include workflow router
app.include_router(workflow_router, prefix="/workflow", tags=["Workflow"])
app.include_router(stream_router, prefix="/stream", tags=["Stream"])