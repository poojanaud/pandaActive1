import os
import json
import base64
import requests
import http.client
from datetime import datetime
from io import BytesIO
from PIL import Image
import openai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Remove load_dotenv() since we're using Cloud Run environment variables
SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_SHOP_NAME = os.getenv("SHOPIFY_SHOP_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_VERSION = "2023-07"

def get_clean_base_url(shop_name: str):
    if not shop_name:
        return ""
    return shop_name.replace(".myshopify.com", "") + ".myshopify.com"

BASE_URL = get_clean_base_url(SHOPIFY_SHOP_NAME)

def fetch_products():
    if not SHOPIFY_API_KEY or not SHOPIFY_SHOP_NAME:
        return {"error": "Shopify API not configured"}
    try:
        endpoint = f"/admin/api/{API_VERSION}/products.json?limit=50"
        conn = http.client.HTTPSConnection(BASE_URL)
        headers = {"X-Shopify-Access-Token": SHOPIFY_API_KEY, "Content-Type": "application/json"}
        conn.request("GET", endpoint, headers=headers)
        response = conn.getresponse()
        if response.status != 200:
            return {"error": f"Failed to fetch products: {response.status}"}
        data = json.loads(response.read().decode())
        return {"products": data.get("products", [])}
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        return {"error": str(e)}

def refine_image_from_data(image_base64: str, prompt: str):
    logger.info("Starting image refinement process")
    
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key missing")
        return {"error": "OpenAI API key missing"}
    
    try:
        # Convert base64 to image
        logger.info("Decoding base64 image")
        image_data = base64.b64decode(image_base64)
        img = Image.open(BytesIO(image_data)).convert("RGBA")
        logger.info(f"Image loaded successfully, size: {img.size}")
        
        # Save to buffer
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        buf.name = "source.png"
        
        # Call OpenAI API
        logger.info("Calling OpenAI API")
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        res = client.images.edit(
            model="gpt-image-1",  # Using the correct model as you mentioned
            image=buf,
            prompt=prompt,
            size="1024x1024",
            n=1,
            timeout=60  # Added timeout to prevent hanging
        )
        
        logger.info(f"OpenAI response received: {res}")
        
        if not res or not res.data:
            logger.error("OpenAI returned no data")
            return {"error": "OpenAI returned no image"}
        
        image_data = res.data[0].b64_json
        if not image_data:
            logger.error("OpenAI returned empty image data")
            return {"error": "OpenAI returned empty image data"}
        
        result = {"image_base64": image_data}
        logger.info(f"Returning image data, size: {len(image_data)} characters")
        return result
        
    except openai.Timeout as e:
        logger.error(f"OpenAI timeout error: {str(e)}")
        return {"error": f"OpenAI API timeout: {str(e)}"}
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return {"error": f"OpenAI API error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {"error": f"Unexpected error: {str(e)}"}

def upload_image_to_shopify(product_id: str, image_base64: str):
    if not SHOPIFY_API_KEY or not SHOPIFY_SHOP_NAME:
        return {"error": "Shopify API not configured"}
    try:
        headers = {
            "X-Shopify-Access-Token": SHOPIFY_API_KEY,
            "User-Agent": "Panda.ai",
            "Content-Type": "application/json"
        }
        payload = {"image": {"attachment": image_base64}}
        
        endpoint = f"/admin/api/{API_VERSION}/products/{product_id}/images.json"
        conn = http.client.HTTPSConnection(BASE_URL)
        conn.request("POST", endpoint, body=json.dumps(payload), headers=headers)
        response = conn.getresponse()
        body = response.read().decode()
        conn.close()
        
        if response.status not in [200, 201]:
            logger.error(f"Upload failed with status: {response.status}")
            return {"error": f"Upload failed: {response.status}"}
        
        logger.info("Image uploaded to Shopify successfully")
        return {"status": "success", "response": json.loads(body)}
    except Exception as e:
        logger.error(f"Error uploading to Shopify: {str(e)}")
        return {"error": str(e)}