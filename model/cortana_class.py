import os
import openai
from cortana.model.text_to_audio import text_to_speech_pyttsx3, text_to_speech_gtts
from cortana.model.audio_to_text import speech_to_text_google, wait_for_call
from cortana.model.predefined_answers import predefined_answers, text_command_detector
import webbrowser
import numpy as np
import pathlib
import os

class cortana():
    def __init__(self, model_name=None,  language='english', role=None, api_key=None,):
        print('------- \n')
        print(f'# Cortana ({language}) \n')
        print('------- \n')
        print('$~~~~~~~~~~~$')
        if api_key is None or api_key=='':
            from api_key import secret_key
            openai.api_key = secret_key
        else:
            openai.api_key = api_key
        # Model to use
        if model_name is not None:
            self.model_name = model_name
        
        # Option of voice
        self.option_talk = None
        self.name = None
        

        # Initialize 
        self.set_language(language)
        self.answers = predefined_answers[language]
        self.reset_messages(role)
        self.log = None

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
        
    def set_model(self, model_name=None):
        if model_name is None:
            print('All models available: \n')
            self.list_model()
            print('----- \n')
            print('Choose the model:')
            model_name = input()
        
        self.model_name = model_name
                
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
            print('-------- \n')
            print(f'{os.getlogin()}: {self.last_input} \n')
            print('----------- \n')
            print(f'Cortana: {self.last_answer} \n')
            print('----------- \n')
            print('$~~~~~~~~~~~$')
            
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
        print(f'Prompt for the image: {self.last_input} \n')
        print('----------------------')
        print('I generated image(s) at the following url(s):\n')
        for url in urls:
            print(str(url)+'\n')
        print('----------- \n')
        print('$~~~~~~~~~~~$')
        # self.messages.append({'role':'assistant', "content":urls})
        # self.image_url = url
        return urls
        
    def voice_cortana(self, text, **kwargs):
        option_talk = kwargs.get('option_talk', 'pyttsx3')
        if self.option_talk is None:
            self.option_talk = option_talk
                
        if self.option_talk=="pyttsx3":
            if self.name is None:
                self.name = kwargs.get('name', 'Zira')
            text_to_speech_pyttsx3(text, self.name)
        elif self.option_talk=="gtts":
            language = self.set_language(kwargs.get('language', self.language))
            text_to_speech_gtts(text, language=language)
    
    def listen_cortana(self, *args, **kwargs):
        self.submit_prompt(*args, **kwargs)
        self.voice_cortana(self.last_answer, **kwargs['voice'])
    
    def cortana_listen(self):
        if self.language == 'english':
            language = 'en-US'
        elif self.language == 'french':
            language = 'fr-FR'
        success=False
        counter=0
        while not success and counter<2:
            counter+=1 # Increment counter
            print(self.answers['listening'])
            response = speech_to_text_google(language)
            success = response['success']
            if success:
                text = response['transcription']
            else:
                text = self.answers['error']
                self.voice_cortana(text)
                text = None
            if response['error'] is not None:
                text = None
        return text, success
    
    def talk_with_cortana(self, **kwargs):
        
        # Language selector
        if self.language == 'english':
            language = 'en-US'
        elif self.language == 'french':
            language = 'fr-FR'
            # For french you must choose google to-text-speech
            if kwargs['voice'].get('option_talk', 'gtts') != 'gtts':
                kwargs['option_talk'] = 'gtts'
        
        # Welcoming message
        self.voice_cortana(self.answers['text_start'], **kwargs['voice'])
        condition = True
        while condition:
            # Get the text from your audio speech
            text, success = self.cortana_listen()
            
            # Check if a specific command has been used
            if text is not None:
                command = text_command_detector(text, self.language)
            else:
                command = None
            
            # Send the text to cortana
            if (command is None) and (text is not None and success):
                self.listen_cortana(text, **kwargs)            
            # Put cortana in pause
            elif (command =='activated_pause') or (text is None):
                self.voice_cortana(self.answers['text_idle'], **kwargs['voice'])
                condition = wait_for_call('Cortana', self.answers['commands']['idle_quit'], language)
                if condition:
                    self.voice_cortana(self.answers['response'], **kwargs['voice'])
            # Shut down cortana
            elif command =='activated_quit':
                condition = False
        self.voice_cortana(self.answers['text_close'])
        print('                  ---- Protocol Terminated ----')
        
    def submit_prompt(self, input_text, **kwargs):
        
        # Check if a specific command has been used
        command = text_command_detector(input_text, self.language)
        
        # If prompt image
        if command is not None:
            if 'prompt_image' in command:
                kwargs = kwargs['image']
                print(self.answers['prompt_image'])
                input_text = input_text.split('Prompt image')[1]
                self.prompt_image(input_text, **kwargs)
                return True
            elif 'exit' in command:
                print(self.answers['text_close'])
                print('                  ---- Protocol Terminated ----')
                return False
            elif 'save' in command:
                self.save_messages()
                print('Saving all messages')
                return True
            else:
                print("I didn't understand your prompt, please reformulate.")
                return True
        else:
            kwargs = kwargs['text']
            self.prompt(input_text, **kwargs)     
            return True

    def save_messages(self):
        # try:
        rnd = np.random.randint(0, 1000000, 1)
        results_dir = pathlib.Path('./results/')
        if not os.path.isdir(results_dir): # Check directory is not existing
            os.makedirs(results_dir) # make that director
        file = open(f'{results_dir}/prompts_{rnd}.txt', 'wt')
        file.write(str(self.messages))
        file.close()
        # except:
        #     print("Unable to write to file")
    
    def show_log(self):
        print(self.log)
    
    def reset_messages(self, role=None):
        if role is None:
            role = self.answers['role']
        self.messages=[{'role': "system", "content":role}]

