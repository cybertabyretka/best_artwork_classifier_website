import logging
import os
from pathlib import Path

import httpx
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .utils import load_artists_mapping

print(Path(__file__).parent.parent)

ARTISTS_MAPPING = load_artists_mapping(Path(__file__).parent.parent / "artists.csv")

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INFERENCE_SERVER_URL = os.getenv("INFERENCE_SERVER_URL")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/predict")
async def predict(request: Request, file: UploadFile = File(...)):
    if not INFERENCE_SERVER_URL:
        logger.error("INFERENCE_SERVER_URL environment variable is not set")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Server configuration error"
        })

    try:
        contents = await file.read()

        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {"file": (file.filename, contents, file.content_type)}
            response = await client.post(
                INFERENCE_SERVER_URL,
                files=files
            )

            response.raise_for_status()
            prediction = response.json()

            class_idx = prediction["class"]
            artist_name = ARTISTS_MAPPING.get(class_idx, f"Unknown artist (class {class_idx})")

            return templates.TemplateResponse("index.html", {
                "request": request,
                "prediction": {
                    **prediction,
                    "artist_name": artist_name,
                    "class_name": artist_name.replace('_', ' ')
                }
            })

    except Exception as e:
        logger.error(f"Error connecting to inference server: {str(e)}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"Ошибка связи с сервером предсказаний: {str(e)}"
        })
