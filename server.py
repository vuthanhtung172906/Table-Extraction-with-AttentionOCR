from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from io import BytesIO
import numpy as np
import prediction

detector1, detector2 = prediction.load_model()


app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_image_into_numpy_array(data):
    return np.array(Image.open(BytesIO(data)))


@app.get("/")
async def root():
    return {"msg": "Hello World"}


@app.post("/upload")
async def getFile(file: UploadFile = File(...)):
    global img
    img = load_image_into_numpy_array(await file.read())
    result = prediction.predict(
        img, detector1, detector2)
    return {"file_name": result}
