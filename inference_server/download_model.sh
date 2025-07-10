#!/bin/bash

if [ -z "$MODEL_FILE_ID" ]; then
    echo "Ошибка: переменная среды MODEL_FILE_ID не установлена" >&2
    exit 1
fi

if [ -z "$MODEL_SHA256" ]; then
    echo "Ошибка: переменная среды MODEL_SHA256 не установлена" >&2
    exit 1
fi

pip install -q gdown

if [ -f "/app/model.onnx" ]; then
    echo "Модель уже существует, пропускаем загрузку"
else
    echo "Загружаем модель с Google Drive..."
    echo "ID файла: $MODEL_FILE_ID"

    gdown "https://drive.google.com/uc?id=$MODEL_FILE_ID" -O /app/model.onnx

    echo "Проверяем целостность файла..."
    echo "Ожидаемый SHA256: $MODEL_SHA256"

    if echo "$MODEL_SHA256  /app/model.onnx" | sha256sum -c -
    then
        echo "Проверка целостности прошла успешно"
    else
        echo "Ошибка: загруженный файл модели не прошел проверку целостности" >&2
        echo "Полученный хеш: $(sha256sum /app/model.onnx | cut -d' ' -f1)" >&2
        exit 1
    fi
fi

echo "Запускаем сервер..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000