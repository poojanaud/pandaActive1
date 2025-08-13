def refine_image_from_data(image_base64: str, prompt: str):
    if not OPENAI_API_KEY:
        return {"error": "OpenAI API key missing"}
    try:
        # Convert base64 to image
        image_data = base64.b64decode(image_base64)
        img = Image.open(BytesIO(image_data)).convert("RGBA")
        
        # Prepare for OpenAI
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        buf.name = "source.png"
        
        # Call OpenAI API with the correct model name
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        res = client.images.edit(
            model="gpt-image-1",  # Using the correct model name as you pointed out
            image=buf,
            prompt=prompt,
            size="1024x1024",
            n=1,
            timeout=60  # Add timeout
        )
        
        if not res or not res.data:
            return {"error": "OpenAI returned no image"}
        
        return {"image_base64": res.data[0].b64_json}
    except Exception as e:
        return {"error": str(e)}