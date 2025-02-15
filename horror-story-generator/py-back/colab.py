!pip install torch torchvision diffusers bitsandbytes accelerate pyngrok nest_asyncio fastapi uvicorn  huggingface_hub --quiet

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
from diffusers import AmusedPipeline
import torch
from huggingface_hub import login
import io
from pyngrok import ngrok
import uvicorn
import nest_asyncio
import getpass
import uuid


nest_asyncio.apply()
# Set your ngrok auth token
NGROK_AUTH_TOKEN = "your auth key"  # Replace with your actual token
ngrok.set_auth_token(NGROK_AUTH_TOKEN)
# Start ngrok tunnel
ngrok_tunnel = ngrok.connect(8000)
public_url = ngrok_tunnel.public_url  # Get the public URL

print(f"Public URL: {public_url}")

# Authenticate with Hugging Face
HUGGING_FACE_TOKEN = getpass.getpass("Enter your Hugging Face Token:")
if HUGGING_FACE_TOKEN:
    login(HUGGING_FACE_TOKEN)
    print("✅ Hugging Face authentication successful!")
else:
    print("❌ Hugging Face token not found! Please enter a valid token.")


# Load the model
pipe = AmusedPipeline.from_pretrained("amused/amused-512", variant="fp16", torch_dtype=torch.float16)
pipe.to("cuda")
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to restrict access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Step 5: Store generated images in memory
image_store = {}

class PromptRequest(BaseModel):
    prompt: str
    negative_prompt: str = "low quality, ugly, deformed, unsymmetrical"

# Step 6: Generate Image (POST Request)
@app.post("/generate")
def generate_image(request: PromptRequest):
    image = pipe(request.prompt, negative_prompt=request.negative_prompt, generator=torch.manual_seed(0)).images[0]

    # Generate unique ID for image
    image_id = str(uuid.uuid4())

    # Convert image to bytes
    img_byte_array = io.BytesIO()
    image.save(img_byte_array, format="PNG")
    img_bytes = img_byte_array.getvalue()

    # Convert image to Base64
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")

    # Store image in memory
    image_store[image_id] = img_bytes

    # Return image URL and Base64
    ngrok_url = ngrok_tunnel.public_url
    return JSONResponse(content={
        "image_url": f"{ngrok_url}/image/{image_id}",
        "image_base64": img_base64
    })

uvicorn.run(app, host="0.0.0.0", port=8000)
