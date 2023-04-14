# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:15:26 2023

@author: ManuMan
"""
import os 
import pyttsx3
from gtts import gTTS
from playsound import playsound
import tempfile
from pydub import AudioSegment

def change_audio_speed(input_filename, output_filename, speed_ratio):
    audio = AudioSegment.from_file(input_filename)
    audio = audio.speedup(playback_speed=speed_ratio)
    audio.export(output_filename, format="mp3")

def text_to_speech_pyttsx3(text, name='Zira'):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    if name=='Zira':
        voice_index=0
    elif name=='David':
        voice_index=1

    engine.setProperty('voice', voices[voice_index].id)
    engine.say(text)
    engine.runAndWait()

def text_to_speech_gtts(text, language='en'):
    tts = gTTS(text, lang=language, slow=False)
    temp_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    tts.save(temp_filename)
    # change_audio_speed(temp_filename, temp_filename, 1.05)  # Augmente la vitesse de lecture de 50%
    playsound(temp_filename)
    os.remove(temp_filename)