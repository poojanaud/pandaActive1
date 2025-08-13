import os
import json
import base64
import requests
import http.client
from datetime import datetime
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image
import openai

load_dotenv()

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
        return {"error": str(e)}

def refine_image(image_url: str, prompt: str):
    if not OPENAI_API_KEY:
        return {"error": "OpenAI API key missing"}

    try:
        # Increase timeout to 60 seconds
        resp = requests.get(image_url, timeout=60)
        resp.raise_for_status()

        img = Image.open(BytesIO(resp.content)).convert("RGBA")
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        buf.name = "source.png"

        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        res = client.images.edit(
            model="dall-e-2",
            image=buf,
            prompt=prompt,
            size="1024x1024",
            n=1,
        )

        if not res or not res.data:
            return {"error": "OpenAI returned no image"}

        return {"image_base64": res.data[0].b64_json}

    except requests.exceptions.Timeout:
        return {"error": "Image download timed out. Please try a different image URL."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to download image: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}

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
            return {"error": f"Upload failed: {response.status}"}

        return {"status": "success", "response": json.loads(body)}

    except Exception as e:
        return {"error": str(e)}
