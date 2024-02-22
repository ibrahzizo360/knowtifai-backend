from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils.transcript import extract_audio, get_transcript, client

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
        audio_path = extract_audio(video_url)
        audio_file = open(audio_path, "rb")
        transcript = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["word"]
        )
        return {"response": transcript}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")
