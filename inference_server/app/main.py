import io
from pathlib import Path
from typing import Dict, Any

import numpy as np
import onnxruntime as ort
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .utils import softmax

app = FastAPI()

ALLOWED_ORIGINS = [
    "https://best-artwork-classifier-website-91vq.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["predict"],
    max_age=600
)

MODEL_PATH = "/app/model.onnx"
if not Path(MODEL_PATH).exists():
    raise RuntimeError(f"Model file not found at {MODEL_PATH}")

model = ort.InferenceSession(MODEL_PATH)
input_name = model.get_inputs()[0].name

PIC_SIZE = (512, 512)
MEAN = np.array([0.485, 0.456, 0.406])
STD = np.array([0.229, 0.224, 0.225])


def preprocess_image(image: Image.Image) -> np.ndarray:
    """
    Perform preprocessing on the input image to replicate
    PyTorch transforms:

    1. Resize to target size
    2. Convert to tensor format (scale pixel values to [0, 1] and rearrange axes)
    3. Normalize using mean and std
    :param image: (Image.Image) The input PIL image.
    :return: np.ndarray The preprocessed image ready for model inference, with shape (1, 3, H, W) and dtype float32.
    """
    image = image.resize(PIC_SIZE)
    img_array = np.array(image, dtype=np.float32)

    img_array = img_array / 255.0
    img_array = np.transpose(img_array, (2, 0, 1))

    img_array = (img_array - MEAN[:, None, None]) / STD[:, None, None]

    img_array = np.expand_dims(img_array, axis=0)
    return img_array.astype(np.float32)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Provides a simple way to check if the server is running and ready
    to accept requests. Typically used for monitoring or deployment
    readiness checks.
    :return: dict A JSON response indicating the server status.
    """
    return {"status": "ready"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Endpoint for performing model inference on an uploaded image.

    Accepts an image file via multipart/form-data, processes it, runs
    inference using an ONNX model, and returns predicted class and probabilities.
    :param file: (UploadFile) Uploaded image file from client.
    :return: dict JSON response.
    """
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    input_data = preprocess_image(image)

    raw_output = model.run(None, {input_name: input_data})[0][0]

    probabilities = softmax(raw_output)
    predicted_class = np.argmax(probabilities)
    confidence = float(probabilities[predicted_class])

    return {
        "class": int(predicted_class),
        "confidence": round(confidence, 2),
        "class_probabilities": probabilities.tolist()
    }
