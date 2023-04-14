import os
import openai
from text_to_audio import text_to_speech_pyttsx3, text_to_speech_gtts
from audio_to_text import speech_to_text_google, wait_for_call
from predefined_answers import predefined_answers, text_command_detector

class cortana():
    def __init__(self, model_name,  language='english', role=None, api_key=None,):
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(f'                           Cortana ({language})')
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        if api_key is None or api_key=='':
            from api_key import secret_key
            openai.api_key = secret_key
        else:
            openai.api_key = api_key
        # Model to use
        self.model_name = model_name
        
        # Option of voice
        self.option_talk = None
        self.name = None
        self.language = language

        # Initialize 
        self.answers = predefined_answers[language]
        self.reset_messages(role)
        self.log = None


    @staticmethod
    def list_model():
        print(openai.Model.list())

    def change_model(self, model_name):
        self.model_name = model_name

    def prompt(self, input_, max_tokens=20, temperature=0.4, **kwargs):
        # Parameters
        print_ = kwargs.get('print', True)
        if not isinstance(input_, str):
            raise Exception(f'input must be of type str, currently is {type(input_)}')
        else:
            self.last_input = input_
        
        # Update message list
        self.messages.append({'role':'user', "content":self.last_input})
        
        # ChatCompletion
        completion = openai.ChatCompletion.create(model=self.model_name,
                                 messages=self.messages,
                                 max_tokens=max_tokens,
                                 temperature=temperature,
                                 **kwargs)
        answer = completion.choices[0].message["content"]
        
        # Update messages
        self.messages.append({'role':'assistant', "content":answer})
        self.log = completion
        self.last_answer = answer
        
        # Print
        if print_:
            print('----------------------')
            pronoun = self.answers['pronoun']
            print(f'{pronoun}: {self.last_input}')
            print('----------------------')
            print(f'Cortana: {self.last_answer}')
            print('****************************')
    
    def voice_cortana(self, text, option_talk='pyttsx3', **kwargs):
        if self.option_talk is None:
            self.option_talk = option_talk
            
        if self.option_talk=="pyttsx3":
            if self.name is None:
                self.name = kwargs.get('name', 'Zira')
            text_to_speech_pyttsx3(text, self.name)
        elif self.option_talk=="gtts":
            if self.language == 'english':
                language = 'en'
            elif self.language == 'french':
                language = 'fr'
            text_to_speech_gtts(text, language=language)
    
    def listen_cortana(self, *args, option_talk="pyttsx3", **kwargs):
        self.prompt(*args, **kwargs)
        self.voice_cortana(self.last_answer, option_talk, **kwargs)
    
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
    
    def talk_with_cortana(self, *args, **kwargs):
        
        # Language selector
        if self.language == 'english':
            language = 'en-US'
        elif self.language == 'french':
            language = 'fr-FR'
            # For french you must choose google to-text-speech
            if kwargs.get('option_talk', 'gtts') != 'gtts':
                kwargs['option_talk'] = 'gtts'
        
        # Welcoming message
        self.voice_cortana(self.answers['text_start'], **kwargs)
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
                self.listen_cortana(text, *args, **kwargs)            
            # Put cortana in pause
            elif (command =='activated_pause') or (text is None):
                self.voice_cortana(self.answers['text_idle'], **kwargs)
                condition = wait_for_call('Cortana', self.answers['commands']['idle_quit'], language)
                if condition:
                    self.voice_cortana(self.answers['response'], **kwargs)
            # Shut down cortana
            elif command =='activated_quit':
                condition = False
        self.voice_cortana(self.answers['text_close'])
        print('                  ---- Protocol Terminated ----')

    def show_log(self):
        print(self.log)
    
    def reset_messages(self, role=None):
        if role is None:
            role = self.answers['role']
        self.messages=[{'role': "system", "content":role}]

def button_click(language, api_key=None, max_tokens=200, option_talk='gtts'):
    name = "gpt-3.5-turbo"
    my_cortana = cortana(name, language, api_key=api_key) 
    my_cortana.talk_with_cortana(max_tokens=max_tokens, option_talk=option_talk)


