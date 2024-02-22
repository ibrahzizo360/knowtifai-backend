from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils.transcript import get_transcript, client, extract_audio_upload_cloudinary, cloudinary_config
import requests
from io import BytesIO
from datetime import datetime
import os

origins = [
    "http://localhost:3000",
    "https://intellisenseai.vercel.app",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/transcript")
async def get_transcript(video_url: str) -> dict:
    try:
        audio_file_link =  extract_audio_upload_cloudinary(video_url, cloudinary_config)
        os.makedirs("/tmp", exist_ok=True)
        fname_local = f"/tmp/{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
        with requests.get(audio_file_link, stream=True) as r:
            with open(fname_local,"wb") as binary_file:
                binary_file.write(r.raw.read())
                
                file_data = open(fname_local,'rb')
                transcript = client.audio.transcriptions.create(
                    file=file_data,
                    model="whisper-1",
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )
                return {"response": transcript}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")
