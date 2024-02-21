from typing import Union, List
from fastapi import HTTPException
from fastapi import FastAPI
from youtube_transcript_api import YouTubeTranscriptApi,NoTranscriptAvailable
from fastapi.middleware.cors import CORSMiddleware

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
def get_transcript(videoId: str) -> dict:
    try:
        response: List[dict] = YouTubeTranscriptApi.get_transcript(videoId)
        return {"transcript": response}
    except NoTranscriptAvailable:
        raise HTTPException(status_code=404, detail="Transcript not available")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")