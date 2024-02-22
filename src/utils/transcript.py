import os
from pytube import YouTube
from dotenv import load_dotenv
import datetime
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def extract_audio(url):
    yt_video = YouTube(url)
    streams = yt_video.streams.filter(only_audio=True).first()
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.mp4'
    streams.download(output_path='tmp/', filename=filename)
    # audio_file_path = os.path.join('audio', filename)
    audio_file_path = 'tmp/' + filename
    return audio_file_path

def get_transcript(audio_file): 
    print(audio_file, "audio file2")
    transcript = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["word"]
        )
    return transcript



    

    
    