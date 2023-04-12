# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:20:38 2023

@author: ManuMan
"""
# import deepspeech
import numpy as np
import pyaudio
import speech_recognition as sr

def wait_for_call(key_start, key_end):
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('==============================================')
        print(f'Idle state, say \'{key_start}\' to activate me...\n')
        print(f'Or, say \'{key_end}\' to deactivate me.')
        print('==============================================')
        while True: 
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio)
                if key_start.lower() in text.lower():
                    return True
                if key_end.lower() in text.lower():
                    return False
            except Exception as e:
                pass
                # print('Please speak again.')

def speech_to_text_sr():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("I am listening...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_sphinx(audio)
        print("You said: ", text)
    except sr.UnknownValueError:
        print("Couldn't understand the audio")
    except sr.RequestError as e:
        print(f"Error: {e}")

def speech_to_text_google():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("I am listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response
