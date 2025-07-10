import httpx
import os
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import logging

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем URL из переменных окружения
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
        # Прочитать содержимое файла
        contents = await file.read()

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Отправляем файл на инференс-сервер
            files = {"file": (file.filename, contents, file.content_type)}
            response = await client.post(
                INFERENCE_SERVER_URL,
                files=files
            )

            # Проверяем статус ответа
            response.raise_for_status()
            prediction = response.json()

            return templates.TemplateResponse("index.html", {
                "request": request,
                "prediction": prediction
            })

    except Exception as e:
        # Логируем полную ошибку
        logger.error(f"Error connecting to inference server: {str(e)}")

        # Возвращаем пользователю понятное сообщение
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"Ошибка связи с сервером предсказаний: {str(e)}"
        })