from fastapi import FastAPI, File, UploadFile
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
from google.cloud import speech
import google.generativeai as genai
from dotenv import load_dotenv
import os

app = FastAPI()

# Load the .env file
load_dotenv()

# Access the API key from the environment
google_api_key = os.getenv("GOOGLE_API_KEY")

# Function to process video upload and audio transcription
def process_video_and_transcribe(file_location):
    # Extract audio from video
    video = VideoFileClip(file_location)
    audio = video.audio
    audio_file = f"{file_location}.mp3"
    audio.write_audiofile(audio_file)

    # Google Cloud Speech API setup
    client = speech.SpeechClient.from_service_account_file('keys.json')
    with open(audio_file, "rb") as f:
        mp3_data = f.read()

    audio_file_obj = speech.RecognitionAudio(content=mp3_data)
    config = speech.RecognitionConfig(
        sample_rate_hertz=44100,
        enable_automatic_punctuation=True,
        language_code="en-US"
    )

    # Transcribe audio
    response = client.recognize(config=config, audio=audio_file_obj)
    if response.results:
        transcript = ' '.join([result.alternatives[0].transcript for result in response.results])
        return transcript
    else:
        return ""


# Route to handle video upload and transcription
@app.post("/upload-video/")
async def upload_video_and_transcribe(file: UploadFile = File(...)):
    file_location = f"received_{file.filename}"
    with open(file_location, "wb") as video_file:
        video_file.write(await file.read())

    # Process video and get transcript
    transcript = process_video_and_transcribe(file_location)

    # Generate content based on transcript using Generative AI
    if transcript:
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel('gemini-pro')
        question = "Rate this content 1 to 10 for kids: " + transcript
        response = model.generate_content(question)
        generated_text = response.text
    else:
        generated_text = "No transcript available."

    return {
        "message": f"Video '{file.filename}' received and transcribed successfully",
        "transcript": transcript,
        "generated_text": generated_text
    }
