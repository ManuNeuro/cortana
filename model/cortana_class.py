import os
import openai
from cortana.model.text_to_audio import text_to_speech_pyttsx3, text_to_speech_TTS, text_to_speech_gtts
from cortana.model.audio_to_text import speech_to_text, stt_whisper, wait_for_call
from cortana.model.predefined_answers import predefined_answers, text_command_detector
import webbrowser
import numpy as np
import pathlib
import os
import json 
import time 

basedir_model = os.path.dirname(__file__)

with open(os.path.join(basedir_model, 'parameters.json')) as json_file:
    kwargs = json.load(json_file)
    
    
class Cortana():
    def __init__(self, model_name=None,  language='english', role='Generic', api_key=None, **kwargs):
        print('-------------------------------------- ')
        print(f'# Cortana + {model_name} ({language}) ')
        print('-------------------------------------- \n')

        if api_key is None or api_key=='':
            from api_key import secret_key
            openai.api_key = secret_key
        else:
            openai.api_key = api_key
        # Model to use
        if model_name is not None:
            self.model_name = model_name

        self.role = role

        # Option of voice
        self.tts_option = None
        self.stt_option = None

        # Initialize 
        self.set_language(language)
        self.answers = predefined_answers[language]
        self.reset_messages()
        self.log = None
        self.flag = True
        
        
    def greetings(self):
        try:
            self.voice_cortana(self.answers['text_start'], **kwargs['voice'])   
        except:
            pass

    def set_language(self, language):
                
        # Language selector
        if language == 'english':
            self.language = language
            self.code_language = 'en-US'
        elif language == 'french':
            self.language = language
            self.code_language = 'fr-FR'
        else:
            raise Exception("{language}, language not supported.")
        return self.code_language
            
    @staticmethod
    def list_model():
        res = openai.Model.list()
        list_name = [model['id'] for model in res['data']]
        print(list_name)
    
    def set_role(self, role):
        self.role = role
        print(f'*>> I changed my role to {self.role}.*')

    def set_model(self, model_name=None):
        if model_name is None:
            print('All models available: ')
            self.list_model()
            print('-----')
            print('Choose the model:')
            model_name = input()
        self.model_name = model_name
        print(f'*>> I changed my model to {self.model_name}.*')

    def prompt(self, input_, _print=True, **kwargs):
        # Parameters
        if not isinstance(input_, str):
            raise Exception(f'input must be of type str, currently is {type(input_)}')
        else:
            self.last_input = input_
        
        # Update message list
        self.messages.append({'role':'user', "content":self.last_input})
        
        # ChatCompletion
        completion = openai.ChatCompletion.create(model=self.model_name,
                                 messages=self.messages,
                                 **kwargs)
        answer = completion.choices[0].message["content"]
        
        # Update messages
        self.completion = completion
        self.messages.append({'role':'assistant', "content":answer})
        self.log = completion
        self.last_answer = answer
        
        # Print
        if _print:
            # pronoun = self.answers['pronoun']
            print('-------- ')
            print(f'{os.getlogin()}: {self.last_input} ')
            print('\n----------- ')
            print(f'Cortana: \n{self.last_answer} ')
            print('\n----------- \n')

    def prompt_image(self, input_, n=5, size="1024x1024", **kwargs):
        
        if not isinstance(input_, str):
            raise Exception(f'input must be of type str, currently is {type(input_)}')
        else:
            self.last_input = input_
        
        # Update message list
        self.messages.append({'role':'user', "content":self.last_input})
        response = openai.Image.create(prompt=self.last_input, n=n, size=size, **kwargs)
        urls = [response['data'][i]['url'] for i in range(n)]
        [webbrowser.open(url, new=0, autoraise=True) for url in urls]  # Go to example.com
        print('----------------------')
        print(f'Prompt for the image: {self.last_input} ')
        print('----------------------')
        print('I generated image(s) at the following url(s):')
        for url in urls:
            print(str(url)+'')
        print('\n----------- ')
        print('$~~~~~~~~~~~$')
        # self.messages.append({'role':'assistant', "content":urls})
        # self.image_url = url
        return urls
        
    def voice_cortana(self, text, **kwargs):
        
        self.tts_option = kwargs['tts'].get('option', 'gtts')
        
        if self.language == 'french':
            if self.tts_option == "pyttsx3": # Can't use pyttsx3 for french, default is gtts
                tts_option = "gtts"
        
        if self.tts_option=="pyttsx3":
            tts_model = kwargs.get('model', 'Zira')
            text_to_speech_pyttsx3(self, text, tts_model)
        elif self.tts_option=="gtts":
            text_to_speech_gtts(self, text, language=self.code_language)
        elif self.tts_option=='tts':
            tts_model = kwargs['tts'].get('model', None)
            text_to_speech_TTS(self, text, language=self.code_language, model=tts_model)
        else:
            raise Exception(f'Text-to-speech {self.tts_option} option is not supported.')
    
    def listen_cortana(self, *args, **kwargs):
        print(self.answers['stt']['text_sending'])
        self.submit_prompt(*args, _voice=True, **kwargs)
        self.voice_cortana(self.last_answer, **kwargs['voice'])
    
    def cortana_listen(self, stt_option='google', nbtrial=2, timeout=4, **kwargs):
        
        self.stt_option = stt_option
        
        condition=True
        error=None
        text = None
        counter=0
        while condition:
            
            if self.flag:
                if stt_option == 'sphinx' or stt_option == 'google': # Only working in english
                    # This option is to be privileged, it is faster, more reliable, and the output is cleaner
                    response = speech_to_text(self, stt_option, self.code_language, timeout)
                elif stt_option == 'whisper':
                    # Please, note this option is not working well and would require further fine tuning
                    model = kwargs.get('model', 'base')
                    response = stt_whisper(model, timeout)
                else:
                    raise Exception(f'Model {stt_option} of speech-to-text recognition not implemented.')
                
                success = response['success']
                text = response['transcription']
                error = response['error']
                
                if success and text is not None:
                    condition = False
                    
                print('response', response)
                    
                if response['error'] is not None:
                    if "No voice detected." != response['error']:
                        nbtrial += 1 # Request not understood, add one more trial
            
                counter+=1 # Increment counter
                if counter>=nbtrial:
                    condition = False
            else:
                condition = False
                
        return text, error
    
    def talk_with_cortana(self, **kwargs):
        print('------- ')
        print(self.answers['active_title'])
        print('------- ')

        stt_option = kwargs['voice']['stt'].get('option', 'google')
        stt_timeout = kwargs['voice']['stt'].get('timeout', 3)
        stt_nbtrial = kwargs['voice']['stt'].get('nbtrial', 2) # Number of trial for the speech-to-text
        stt_model = kwargs['voice']['stt'].get('model', 'base')
        
        # Language selector
        if self.language == 'french':
            # For french you can't use pyttsx3 ! Default gtts will be used.
            if kwargs['voice']['stt'].get('option', 'gtts') == 'pyttsx3':
                kwargs['stt_option'] = 'gtts'
        
        # Welcoming message
        self.voice_cortana(self.answers['active_mode'], **kwargs['voice'])
        condition = True
        while condition:
            # Get the text from your audio speech
            text, error = self.cortana_listen(stt_option=stt_option, nbtrial=stt_nbtrial, 
                                                       timeout=stt_timeout, model=stt_model)
            
            # Check if a specific command has been used
            if text is not None:
                command = text_command_detector(text, self.language)
            else:
                command = ''
            
            print('command', command)
            
            # Send the text to cortana
            if self.flag:
                # Put cortana in pause
                if command == 'activated_exit':
                    condition = False
                elif (command == 'activated_pause') or ("No voice detected." == error):
                    self.voice_cortana(self.answers['text_idle'], **kwargs['voice'])
                    condition = wait_for_call(self, self.answers['commands']['idle_start'], self.answers['commands']['idle_exit'], self.code_language)
                    if condition:
                        self.voice_cortana(self.answers['response'], **kwargs['voice'])
                elif (command is None) and (text is not None and error is None):
                    self.listen_cortana(text, **kwargs) 
            else:
                condition = False
        self.voice_cortana(self.answers['text_close'], **kwargs['voice'])
        time.sleep(2)
        print(self.answers['protocol_terminated'])
        self.flag = False
        
        
    def submit_prompt(self, input_text, _voice=False, preprompt_path='./model/preprompt.json', **kwargs):# ./model/preprompt.json
        
        # Check if a specific command has been used
        command = text_command_detector(input_text, self.language)

        with open(preprompt_path) as json_file:
            preprompt = json.load(json_file)
            
        model_spec = f' If prompted which model you use: I use OpenAI model: {self.model_name}.'
        if not _voice: # Specific preprompt when generating text (no audio)
            self.messages.append({'role': "system", "content":'Your specific role for this question is: '+preprompt['roles'][self.role]+\
                                  '. If requested by the user, provide your specific role. '+preprompt['text']+model_spec})
        else:
            self.messages.append({'role': "system", "content":'Your specific role for this question is: '+preprompt['roles'][self.role]+\
                                  '. If requested by the user, provide your specific role. '+preprompt['voice']+model_spec})
        # Issue: this is suboptimal because it's going to be sent at each request, consuming token for redundant information. 
        # However, this is needed for being able to change role at each questions. 
        # ToDo: fine a simpler way to only send in new roles, and not recall the role at each request.
        
        # If prompt image
        if command is not None:
            if 'prompt_image' in command:
                kwargs = kwargs['image']
                print(self.answers['prompt_image'])
                input_text = input_text.split('Prompt image')[1]
                self.prompt_image(input_text, **kwargs)
                return True
            else:
                print("I didn't understand your prompt, please reformulate.")
                return True
        else:
            kwargs = kwargs['text']
            self.prompt(input_text, **kwargs)     
            return True

    def show_log(self):
        print(self.log)
    
    def reset_messages(self, role=None):
        if role is None:
            role = self.answers['role']
        self.messages=[{'role': "system", "content":role}]
        
    def __del__(self):
        if hasattr(self, 'spinner'): # If spinner is still running, stop it
            if self.spinner.running:           
                self.spinner.stop()  

# my_cortana = Cortana('gpt-4', 'english')
# my_cortana.talk_with_cortana(**kwargs)