# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 20:46:39 2023

@author: ManuMan
"""
import os
import json 
basedir_answer = os.path.dirname(__file__)

with open(os.path.join(basedir_answer, 'preprompt.json')) as json_file:
    kwargs = json.load(json_file)

predefined_answers = {'english':{'error':"Sorry, I did not understood your request.",
                                 'text_start':"Hello, I am Cortana, your smart assistant, how can I help you?",
                                 'text_idle':"I am putting myself into IDLE, wake me, when you need me.",
                                 'text_close':"I am shutting down my systems, bye",
                                 'prompt_image':"Please wait, I will generate an image",
                                 'role':kwargs['persona'] + ' You have to speak in english.',
                                 'active_mode': "Active mode activated, let's chat!",
                                 'response':"yes",
                                 'language':'en-US',
                                 'commands':{'exit':'Shut Down',
                                             'idle_quit':'Activate',
                                             'activated_pause':'Cortana inactive',
                                             'activated_quit':'Cortana Shut Down',
                                             'prompt_image':"Prompt image"},
                                 'pronoun':'Me',
                                 'listening':"I am listening...",},
                    'french':{'error':"Désolé, je n'ai pas compris votre question.",
                              'text_start':"Bonjour, je suis cortana, votre assistant intelligent personnel, comment puis-je vous aider?",
                              'active_mode': "Mode de discussion interactif activé!",
                              'text_idle':"Je met mon système en veille, réveillez-moi, quand vous avez besoin.",
                              'text_close':"Je termine mon protocole, au revoir",
                              'prompt_image':"Veuillez patienter, je vais générer une image.",
                              'role':kwargs['persona'] + ' You have to speak in french.',
                              'response':'Oui',
                              'language':'fr-FR',
                              'commands':{'exit':'Fermeture',
                                          'idle_quit':'Activation',
                                          'activated_pause':'Cortana Veille',
                                          'activated_quit':'Cortana Fermeture',
                                          'prompt_image':"Générer image"},
                              'pronoun':'Moi',
                              'listening':"J'écoute...",}
                    }


def command_condition(text, command):
    if command.lower() in text.lower():
        return True
    else:
        return False

def text_command_detector(text, language):
    commands = predefined_answers[language]['commands']
    for command, text_command in commands.items():
        if 'activated' in command:
            if command_condition(text, text_command):
                return command
        elif 'image' in command:
            if command_condition(text, text_command):
                return command
        elif 'exit' in command:
            if command_condition(text, text_command):
                return command
        elif 'save' in command:
            if command_condition(text, text_command):
                return command
    return None

