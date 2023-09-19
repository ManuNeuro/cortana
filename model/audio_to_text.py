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
import webrtcvad
import numpy as np 
import audioop
import tqdm

from cortana.model.external_classes import Spinner
from cortana.model.predefined_answers import idle_english, idle_french

# vad = webrtcvad.Vad()
# vad.set_mode(2)

def wait_for_call(self, key_start, key_end, language, timeout=4):
    
    recognizer = sr.Recognizer()
    
    # Condition to stop loop
    condition = True
    counter = 0
    
    with sr.Microphone() as source:
        if 'en' in language:
            idle_english(key_start, key_end)
        elif 'fr' in language:
            idle_french(key_start, key_end)
        counter = 0
        while condition: 
            recognizer.adjust_for_ambient_noise(source)
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n')
            self.spinner = Spinner(message=self.answers['stt']['recording'])
            self.spinner.start()
            try:
                audio = recognizer.listen(source, timeout=5)
                success = True
            except:
                success = False
                print('>> #{0} {1}'.format(counter, self.answers['stt']['idle_err1']))
            self.spinner.stop()
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n')                
            if success:
                try:
                    text = recognizer.recognize_google(audio, language=language)
                    if key_start.lower() in text.lower():
                        print('>> #{0} {1}'.format(counter, self.answers['stt']['idle_start']))
                        return True
                    if key_end.lower() in text.lower():
                        print('>> #{0} {1}'.format(counter, self.answers['stt']['idle_exit']))
                        return False
                except Exception as e:
                    print('>> #{0} {1}'.format(counter, self.answers['stt']['idle_err2']))
            
            if not self.flag:
                condition = False
            
            counter += 1
            
            
def stt_sphinx(self, language, timeout=4):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source,timeout=timeout)
    print(self.answers['stt']['rec_complete'])

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = recognizer.recognize_sphinx(audio, language=language)
        print(self.answers['stt']['trans_complete'])
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"
        print(f'>> Error: {response["error"]}')

    return response


def stt_model_selector(recognizer, audio, option, **kwargs):
    
    if option == 'google':
        return recognizer.recognize_google(audio, **kwargs)
    elif option == 'sphinx':
        return recognizer.recognize_sphinx(audio, **kwargs)

def speech_to_text(self, option, language, timeout):

    recognizer = sr.Recognizer()
        
    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }
    try:
        # Record audio
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')
            spinner = Spinner(message=self.answers['stt']['recording'])
            spinner.start()
            audio = recognizer.listen(source, timeout=timeout)
            spinner.stop()
            print('')
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            print(self.answers['stt']['rec_complete'])
            buffer = source.stream.read(source.CHUNK)
            energy = audioop.rms(buffer, source.SAMPLE_WIDTH)  # energy of the audio signal
        
        threshold = recognizer.energy_threshold*0.65
        # print(voice_detector(audio), threshold)
        if voice_detector(audio) < threshold*1.05: # If no voice is detected
            response["error"] = "No voice detected."
            response["success"] = False
            print(f'>> Error: {response["error"]}')
        else:
            # Transcribe
            try:
                response["transcription"] = stt_model_selector(recognizer, audio, option, language=language)
                print(self.answers['stt']['trans_complete'])
            except sr.RequestError:
                response["success"] = False
                response["error"] = self.answers['stt']['api_error']
                print(f'>> Error: {response["error"]} ')
            except sr.UnknownValueError:
                # speech was unintelligible
                response["error"] = self.answers['stt']['error_speech']
                print(f'>> Error: {response["error"]} ')
            
    except Exception as e:
        spinner.stop()
        response["error"] = f'An error occured: {e}'
        print(f'>> Error: {response["error"]} ')
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        
    return response

def record_audio(timeout=4):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=timeout)
        print(">> Recording complete!")
    
    # save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with open(temp_file.name, "wb") as file:
        file.write(audio.get_wav_data())
    # print("Saved to: ", temp_file.name)

    return temp_file.name

def voice_detector(audio):
    audio_arr = np.frombuffer(audio.frame_data, dtype=np.int16)
    mean = np.mean(abs(audio_arr))
    return mean

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
        print('>> Recording, please speak!')
        result = ws.transcribe(model, audio_file, fp16=False)
        response["transcription"] = result['text']
        print(">> Transcription complete!")
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