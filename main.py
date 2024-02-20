from typing import Union

from fastapi import FastAPI
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",
    "http://localhost:8080",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/transcript")
def get_transcript(videoId: str):
    try:
        response = YouTubeTranscriptApi.get_transcript(videoId)
    except(Exception):
        print(Exception)
        response = "No transcript available"
        
    return {"transcript": response}
