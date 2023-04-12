# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:15:26 2023

@author: ManuMan
"""
import os 
import pyttsx3
from gtts import gTTS
from playsound import playsound

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
    tts = gTTS(text, lang=language)
    tts.save("temp.mp3")
    playsound("temp.mp3")
    os.remove("temp.mp3")