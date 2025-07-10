from fastapi import FastAPI, File, UploadFile
import numpy as np
from PIL import Image
import onnxruntime as ort
import io

app = FastAPI()

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
    Репликация PyTorch-преобразований:
    1. Resize
    2. ToTensor (деление на 255 + изменение порядка осей)
    3. Normalize
    """
    image = image.resize(PIC_SIZE)
    img_array = np.array(image, dtype=np.float32)

    img_array = img_array / 255.0
    img_array = np.transpose(img_array, (2, 0, 1))

    img_array = (img_array - MEAN[:, None, None]) / STD[:, None, None]

    img_array = np.expand_dims(img_array, axis=0)
    return img_array.astype(np.float32)


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """API endpoint для предсказаний"""
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    input_data = preprocess_image(image)

    results = model.run(None, {input_name: input_data})[0]
    predicted_class = np.argmax(results)
    confidence = float(results[0][predicted_class])

    return {
        "class": int(predicted_class),
        "confidence": confidence,
        "class_probs": results.tolist()
    }
