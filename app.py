from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel
from demoPanda_api import (
    fetch_products, 
    refine_image_from_data, 
    upload_image_to_shopify,
    get_openai_credit_balance
)

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

# Request models
class RefineImageRequest(BaseModel):
    image_base64: str
    prompt: str

class UploadImageRequest(BaseModel):
    product_id: str
    image_base64: str

@app.get("/")
def root():
    return {"status": "PandaAI API running!"}

@app.get("/fetch_products")
def get_products():
    return fetch_products()

@app.post("/refine_image")
def refine_image_endpoint(request: RefineImageRequest):
    try:
        result = refine_image_from_data(request.image_base64, request.prompt)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/upload_image")
def upload_image_endpoint(request: UploadImageRequest):
    try:
        result = upload_image_to_shopify(request.product_id, request.image_base64)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.get("/openai_credit_balance")
def openai_credit_balance():
    try:
        result = get_openai_credit_balance()
        return result
    except Exception as e:
        return {"error": str(e)}