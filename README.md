# Artwork Classifier Website

[![Render Status](https://img.shields.io/badge/Render-Online-brightgreen)](https://best-artwork-classifier-website-91vq.onrender.com)

A web application for classifying artworks by artist. Users upload an image, and the model predicts which of 50 artists it belongs to.

## Links

- Website: [Deployment Link](https://best-artwork-classifier-website-91vq.onrender.com)

## Features

- Upload images via a web interface
- AI-based artist classification
- Microservice architecture
- Result caching with Redis (TTL = 10 minutes)
- Docker containerization
- Automatic deployment on Render.com

## Technologies

- **Web Server**:
  - Python 3.9
  - FastAPI
  - Jinja2 (templating)
  - HTTpx (HTTP client)

- **Inference Server**:
  - ONNX Runtime
  - Pillow (image processing)
  - NumPy
  - aioredis (async Redis client)

- **Infrastructure**:
  - Docker
  - Render.com (cloud hosting)
  - Google Drive (model storage)
  - Redis (caching layer)

## How It Works

1. The user uploads an image via the web interface
2. The web server sends the image to the inference server
3. The inference server processes the image and makes a prediction
4. The result (artist and confidence score) is returned to the user

## Running the Service

Make sure you have Docker and Docker Compose installed. From the root of the project (where your `docker-compose.yml` lives), run:

```bash
# Build images and start containers in detached mode
docker-compose up --build -d

# View logs (optional)
docker-compose logs -f

# Stop and remove containers, networks, and volumes
docker-compose down
```