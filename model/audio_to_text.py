# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:20:38 2023

@author: ManuMan
"""
# import deepspeech
import speech_recognition as sr
import whisper as ws
import tempfile
import os

idle_english = lambda key_start, key_end:print(f"============================================== \
                                               Idle state, say \'{key_start}\' to activate me...\n   \
                                               Or, say \'{key_end}\' to deactivate me. \
                                               ==============================================")
idle_french = lambda key_start, key_end:print(f"============================================== \
                                              État de veille, dites \'{key_start}\' pour me réveiller...\n \
                                              Ou dites \'{key_end}\' pour me désactiver. \
                                              ==============================================")

def wait_for_call(self, key_start, key_end, language, timeout=4):
    r = sr.Recognizer()
    
    # Condition to stop loop
    condition = True
    counter = 0
    
    with sr.Microphone() as source:
        if 'en' in language:
            idle_english(key_start, key_end)
        elif 'fr' in language:
            idle_french(key_start, key_end)
        while condition and self.flag: 
            audio = r.listen(source, timeout=timeout, phrase_time_limit=None)
            try:
                text = r.recognize_google(audio, language=language)
                if key_start.lower() in text.lower():
                    return True
                if key_end.lower() in text.lower():
                    return False
            except Exception as e:
                pass
                # print('Command not recognized.')

def stt_sphinx(timeout=4):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source,timeout=timeout)
        print("*>> Recording complete!*")

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = recognizer.recognize_sphinx(audio)
        print("*>> Transcription complete!*")
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response
        

def stt_google(language, timeout):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=timeout)
        print("*>> Recording complete!*")
        
    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = recognizer.recognize_google(audio, language=language)
        print("*>> Transcription complete!*")
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response

def record_audio(timeout=4):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=timeout)
        print("*>> Recording complete!*")
    
    # save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with open(temp_file.name, "wb") as file:
        file.write(audio.get_wav_data())
    # print("Saved to: ", temp_file.name)

    return temp_file.name

def stt_whisper(model='base', timeout=4):
    '''
    For using cuda see
    https://stackoverflow.com/questions/75908422/whisper-ai-error-fp16-is-not-supported-on-cpu-using-fp32-instead
    '''
    model = ws.load_model(model)
    audio_file = record_audio(timeout)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        result = ws.transcribe(model, audio_file, fp16=False)
        response["transcription"] = result['text']
        print("*>> Transcription complete!*")
    except Exception as e:
        response["success"] = False
        response["error"] = str('An error occured:', e)
    if result['text'] == '':
        response["success"] = False
        response["error"] = "Unable to recognize speech"

    # clean up temporary file
    # print("Deleting temporary file: ", audio_file)
    os.remove(audio_file)

    return response