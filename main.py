import base64
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from libs.psql import db

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:1313",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await db.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/image/{data}")
async def get_image(data: str):
    img_data = json.loads(base64.urlsafe_b64decode(data + '=' * (4 - len(data) % 4)))
    return FileResponse(img_data['path'])


@app.get("/image-url")
async def get_image_url():
    res = await db.fetch_one('select description, path, year from images order by random() limit 1')
    if res is None:
        return None
    img_data = {'path': res._mapping['path'], 'year': res._mapping['year']}
    tmp = base64.urlsafe_b64encode(json.dumps(img_data).encode()).rstrip(b'=')
    return {'url': f'http://127.0.0.1:8000/image/{tmp.decode()}'}


class Image(BaseModel):
    url: str


@app.post('/check-year')
async def check_image(image: Image):
    endoded_data = image.url.split('/')[-1]
    endoded_data = endoded_data + '=' * (len(endoded_data) % 4)
    img_data = json.loads(base64.urlsafe_b64decode(endoded_data))
    return await db.fetch_one('select year from images where id = :id', {'id': img_data['id']})


@app.get('/game')
async def get_game(rounds: int):
    if rounds < 1:
        return None
    res = await db.fetch_all('select id, path from images order by random() limit 1')
    images = []
    for i in res:
        img_data = {'path': i._mapping['path'], 'id': i._mapping['id']}
        tmp = base64.urlsafe_b64encode(json.dumps(img_data).encode()).rstrip(b'=')
        images.append({'url': f'http://127.0.0.1:8000/image/{tmp.decode()}'})
    return images
