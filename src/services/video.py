import os
from dotenv import load_dotenv
from openai import OpenAI
import cloudinary
import cloudinary.uploader
import cloudinary.api
import pytube
from datetime import datetime

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_audio_path(url: str):
    try:
        # Download only the audio stream
        audio_stream = pytube.YouTube(url).streams.filter(only_audio=True).first()

        # Generate a unique filename with timestamp
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}"

        audio_stream.download(filename=filename, output_path='/tmp/')

        audio_file_path = '/tmp/' + filename

        return audio_file_path

    except (pytube.exceptions.PytubeError, ValueError) as e:
        print(e, "error")
        raise ValueError(f"Failed to extract audio from '{url}': {e}")
    except Exception as e:
        raise Exception(f"Error uploading audio to Cloudinary: {e}")
    
    
def get_transcript(audio_file): 
    print(audio_file, "audio file2")
    transcript = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["word"]
        )
    return transcript