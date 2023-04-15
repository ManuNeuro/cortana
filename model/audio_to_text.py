# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:20:38 2023

@author: ManuMan
"""
# import deepspeech
import numpy as np
import pyaudio
import speech_recognition as sr


idle_english = lambda key_start, key_end:print(f"============================================== \
                                               Idle state, say \'{key_start}\' to activate me...\n   \
                                               Or, say \'{key_end}\' to deactivate me. \
                                               ==============================================")
idle_french = lambda key_start, key_end:print(f"============================================== \
                                              État de veille, dites \'{key_start}\' pour me réveiller...\n \
                                              Ou dites \'{key_end}\' pour me désactiver. \
                                              ==============================================")

def wait_for_call(key_start, key_end, language, loop='bool'):
    r = sr.Recognizer()
    
    # Condition to stop loop
    condition = True
    counter = 0
    
    with sr.Microphone() as source:
        if 'en' in language:
            idle_english(key_start, key_end)
        elif 'fr' in language:
            idle_french(key_start, key_end)
        while condition: 
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio, language=language)
                if key_start.lower() in text.lower():
                    return True
                if key_end.lower() in text.lower():
                    return False
            except Exception as e:
                pass
                # print('Command not recognized.')

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

def speech_to_text_google(language):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = recognizer.recognize_google(audio, language=language)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response
