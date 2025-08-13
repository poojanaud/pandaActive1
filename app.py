from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel
from demoPanda_api import refine_image_from_data

app = FastAPI()

# CORS Configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://developmentpanda-468723.web.app")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

class RefineImageRequest(BaseModel):
    product_id: str
    image_base64: str
    prompt: str

@app.get("/")
def root():
    return {"status": "PandaAI API running!"}

@app.post("/refine_image")
def refine_image_endpoint(request: RefineImageRequest):
    try:
        result = refine_image_from_data(request.image_base64, request.prompt)
        return result
    except Exception as e:
        return {"error": str(e)}