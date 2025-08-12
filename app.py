from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import after setting environment variables
os.environ["PYTHONPATH"] = "/app"

from demoPanda_api import (
    fetch_products,
    refine_image,
    upload_image_to_shopify,
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

@app.get("/")
def root():
    return {"status": "PandaAI API running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/fetch_products")
def get_products():
    return fetch_products()

@app.post("/refine_image")
def refine(product_id: str, image_url: str, prompt: str):
    return refine_image(image_url, prompt)

@app.post("/upload_image")
def upload(product_id: str, image_base64: str):
    return upload_image_to_shopify(product_id, image_base64)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)