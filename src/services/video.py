import os
from dotenv import load_dotenv
from openai import OpenAI
import cloudinary
import cloudinary.uploader
import cloudinary.api
import pytube
from datetime import datetime
import yt_dlp
import io
import boto3
from botocore.exceptions import ClientError

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

async def get_transcript(url: str):
    try:
        # Use yt-dlp to download only the audio stream
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '/tmp/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            audio_file_path = ydl.prepare_filename(info_dict).replace('.webm', '.mp3')
            
        with open(audio_file_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        
        # Create a buffer with the audio data
        buffer = io.BytesIO(audio_data)
        buffer.name = "file.mp3"
            
        transcript = client.audio.transcriptions.create(
            file=buffer,
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["segment"]
        )

        return transcript

    
    
    except (pytube.exceptions.PytubeError, ValueError) as e:
        print(e, "error")
        raise ValueError(f"Failed to extract audio from '{url}': {e}")
    except Exception as e:
        raise Exception(f"Error uploading video: {e}")
    
    


AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')


async def upload_transcript_to_aws(file_name, bucket = AWS_S3_BUCKET_NAME, object_name=None):
    """Upload document to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client(
        service_name='s3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    try:
        s3_client.upload_file(file_name, bucket, object_name)
        url = f"https://{bucket}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
        return url
    except ClientError as e:
        print(e)



