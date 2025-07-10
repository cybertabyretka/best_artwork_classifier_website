from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
import os
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


INFERENCE_SERVER_URL = os.getenv("INFERENCE_SERVER_URL", "http://localhost:8000/predict")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/predict")
async def predict(request: Request, file: UploadFile = File(...)):
    """Отправка изображения на инференс-сервер"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                INFERENCE_SERVER_URL,
                files={"file": (file.filename, await file.read(), file.content_type)}
            )
            response.raise_for_status()
            prediction = response.json()
        except (httpx.HTTPError, httpx.RequestError) as exc:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "error": f"Ошибка связи с сервером предсказаний: {str(exc)}"
            })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "prediction": prediction
    })
