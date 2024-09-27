from fastapi import FastAPI, File, UploadFile
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
from google.cloud import speech
import google.generativeai as genai

