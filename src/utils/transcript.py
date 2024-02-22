import os
from dotenv import load_dotenv
from openai import OpenAI
import cloudinary
import cloudinary.uploader
import cloudinary.api
import pytube
from datetime import datetime

load_dotenv()

cloudinary_config = {
        "cloud_name" : "zizo-dev", 
  "api_key" :"898186636739338", 
  "api_secret" : os.getenv('CLOUDINARY_API_SECRET'), 
    }



client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))



def extract_audio_upload_cloudinary(url: str, cloudinary_config: dict) -> str:
    """
    Extracts audio from a YouTube video URL, uploads it to Cloudinary, and returns the public URL.

    Args:
        url: The YouTube video URL.
        cloudinary_config: A dictionary containing your Cloudinary configuration details.

    Returns:
        The public URL of the uploaded audio file.

    Raises:
        ValueError: If the video URL is invalid or the audio extraction fails.
        Exception: If there's an error uploading to Cloudinary.
    """

    try:
        # Download only the audio stream
        audio_stream = pytube.YouTube(url).streams.filter(only_audio=True).first()

        # Generate a unique filename with timestamp
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
        parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

        # Define the relative path to the tmp directory
        output_path = os.path.join(parent_dir, 'tmp')

        # Check if the directory exists, if not, create it
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        audio_stream.download(filename=filename, output_path=output_path)

        audio_file_path = os.path.join(output_path, filename)

    
        with open(audio_file_path, "rb") as temp_file_reader:
            response = cloudinary.uploader.upload(
                temp_file_reader, public_id=filename, resource_type="video",
                folder="audio", **cloudinary_config
            )

        print("road to success")
        return response["secure_url"]

    except (pytube.exceptions.PytubeError, ValueError) as e:
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



    

    
    