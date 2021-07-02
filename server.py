from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from io import BytesIO
import numpy as np
from requests.api import head
import prediction
import prediction2
from pdf2image import convert_from_bytes
import cv2
detector1, detector2, craft = prediction.load_model()


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
    print(file.filename.split('.')[1])
    global img
    if file.filename.split('.')[1] == 'pdf':
        images = await file.read()
        images = convert_from_bytes(images)
        sheets = []
        for index, image in enumerate(images):
            img = np.array(image)
            img = cv2.resize(img, (1240, 1755))
            try:
                # img = load_image_into_numpy_array(await file.read())
                result, headerData = prediction.predict(
                    img, detector1, detector2, craft)
                sheets.append([result, headerData])
            except:
                try:
                    print("error when run page " + str(index+1))
                    result = prediction2.predict(
                        img, detector1, detector2)
                    headerData = []
                    sheets.append([result, headerData])
                except:
                    pass
        return {"sheets": sheets}
    else:
        img = load_image_into_numpy_array(await file.read())
        try:
            result, headerData = prediction.predict(
                img, detector1, detector2, craft)
            return {"file_name": result, "header_data": headerData}
        except:
            print("error when extrac")
            result, headerData = prediction2.predict(
                img, detector1, detector2)
            headerData = []
            return {"file_name": result, "header_data": headerData}
