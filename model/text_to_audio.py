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
from TTS.api import TTS
import pycountry
from IPython.display import Audio

def get_language_TTS():
    languages = set()

    for model_name in TTS().list_models():
      country_code = model_name.split("/")[1]
      country_language = pycountry.languages.get(alpha_2=country_code)
      if country_language is not None:
        print("{0}: {1}".format(country_language.name, model_name))
        languages.add(country_language.name)
    
    print()
    print("Unique Languages ({0}):".format(len(languages)))
    print(languages)

def text_to_speech_TTS(text, language='en', model=None, vocoder_path=None, **kwargs):
    # https://www.cloudbooklet.com/coquitts-a-python-library-for-text-to-speech/
    # https://huggingface.co/mbarnig/lb-de-fr-en-pt-coqui-vits-tts
    
    file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    if model is None:
            if 'fr' in language:
                # model = 'tts_models/fr/css10/vits'
                model = 'tts_models/multilingual/multi-dataset/your_tts'
                vocoder_path='vocoder_models/universal/libri-tts/wavegrad'
                tts = TTS(model_name=model, progress_bar=True, gpu=False,
                          vocoder_path=vocoder_path)
                file_path = tts.tts_to_file(text=text, file_path=file_path, 
                                            speaker='female-en-5\n', language='fr-fr')
                
            elif 'en' in language:
                model = 'tts_models/en/ljspeech/tacotron2-DCA'
                # vocoder_path='vocoder_models/en/ljspeech/hifigan_v2'
                tts = TTS(model_name=model, progress_bar=True, gpu=False)
                file_path = tts.tts_to_file(text=text, file_path=file_path)
    else:
        if kwargs is None:
            kwargs = {'model':{}, 'tts':{}}
        tts = TTS(model_name=model, 
                  vocoder_path=vocoder_path,
                  **kwargs['model'])
        file_path = tts.tts_to_file(text=text, file_path=file_path, **kwargs['tts'])
    
    # Read and delete audio
    playsound(file_path)
    os.remove(file_path)

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
    engine.setProperty('rate', 135)
    engine.say(text)
    engine.runAndWait()

def text_to_speech_gtts(text, language='en'):
    tts = gTTS(text, lang=language, slow=False)
    temp_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    tts.save(temp_filename)
    # change_audio_speed(temp_filename, temp_filename, 1.05)  # Augmente la vitesse de lecture de 50%
    playsound(temp_filename)
    os.remove(temp_filename)

