FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

COPY download_model.sh .
RUN chmod +x download_model.sh

EXPOSE 8000

CMD ["./download_model.sh"]