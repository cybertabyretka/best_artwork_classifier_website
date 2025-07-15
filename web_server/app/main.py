import base64
import logging
import os
from pathlib import Path

import httpx
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .utils import ARTISTS_MAPPING

app = FastAPI()
BASE_DIR = Path(__file__).parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

templates = Jinja2Templates(directory=BASE_DIR / "templates")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INFERENCE_SERVER_URL = os.getenv("INFERENCE_SERVER_URL")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """
    Serve the home page of the application.

    Renders the index.html template.
    :param request: (Request) The incoming HTTP request.
    :return: HTMLResponse Rendered HTML response.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.get(f"{INFERENCE_SERVER_URL.split('/')[0]}/health")
    except Exception as e:
        logger.warning(f"Warm-up failed: {str(e)}")
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/predict")
async def predict(request: Request, file: UploadFile = File(...)) -> HTMLResponse:
    """
    Handle image upload and send it to the inference server for prediction.

    Reads the uploaded file, forwards it to the inference API, and renders
    the result on the home page. Handles server errors gracefully.
    :param request: (Request) The incoming HTTP request.
    :param file: (UploadFile) Uploaded image file from the client.
    :return: HTMLResponse Rendered HTML response containing either prediction results or an error message.
    """
    if not INFERENCE_SERVER_URL:
        logger.error("INFERENCE_SERVER_URL environment variable is not set")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Server configuration error"
        })

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            await client.get(f"{INFERENCE_SERVER_URL.split('/')[0]}/health")
    except Exception as e:
        logger.warning(f"Warm-up failed: {str(e)}")

    try:
        contents = await file.read()

        base64_bytes = base64.b64encode(contents)
        base64_str = base64_bytes.decode('utf-8')
        data_uri = f"data:{file.content_type};base64,{base64_str}"

        async with httpx.AsyncClient(timeout=60.0) as client:
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
                },
                "image_data": data_uri,
            })

    except Exception as e:
        logger.error(f"Error connecting to inference server: {str(e)}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"Ошибка связи с сервером предсказаний: {str(e)}"
        })
