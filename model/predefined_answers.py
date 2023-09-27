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
                                 'persona':kwargs['persona'] + ' You have to speak in english.',
                                 'active_mode': "Active mode activated, let's chat!",
                                 'active_title':'# Active mode: online discussion with Cortana',
                                 'response':"Yes",
                                 'language':'en-US',
                                 'tts':{'processing':'>> Processing text to speech.',
                                        'reading':'>> Reading audio now.'},
                                 'stt':{'recording':'>> Recording, please speak!      ',
                                        'rec_complete':">> Recording complete!",
                                        'trans_complete':">> Transcription complete!",
                                        'api_error':"API unavailable",
                                        'error_speech':"Unable to recognize speech",
                                        'idle_err1':"idle mode. No command yet, or command not recognized.",
                                        'idle_err2':"idle mode. No voice detected, or command not recognize.",
                                        'idle_wake':"Command recognized: back to active mode.",
                                        'idle_exit':"Command recognized: exiting active mode.",
                                        'text_sending':">> Sending text to OpenAi servers."},
                                 'commands':{'activated_pause':'Cortana inactive',
                                             'activated_exit':'Cortana Shut Down',
                                             'idle_exit':'Shut Down',
                                             'idle_start':'Activate',
                                             'prompt_image':"Prompt image",
                                             'langchain_tools':"Prompt tools"},
                                 'pronoun':'Me',
                                 'listening':"I am listening...",
                                 'protocol_terminated':'          ---- Protocol Terminated ----'},
                    'french':{'error':"Désolé, je n'ai pas compris votre question.",
                              'text_start':"Bonjour, je suis cortana, votre assistant intelligent personnel, comment puis-je vous aider?",
                              'active_mode': "Mode de discussion interactif activé!",
                              'active_title':'# Mode actif: discussion orale avec Cortana',
                              'text_idle':"Je met mon système en veille, réveillez-moi, quand vous avez besoin.",
                              'text_close':"Je termine mon protocole, au revoir",
                              'prompt_image':"Veuillez patienter, je vais générer une image.",
                              'persona':kwargs['persona'] + ' You have to speak in french.',
                              'response':'Oui',
                              'language':'fr-FR',
                              'tts':{'processing':'>> Transcription texte vers audio.',
                                     'reading':">> Lecture de l'audio'."},
                              'stt':{'recording':'>> Enregistrement en cours, parlez !      ',
                                     'rec_complete':">> Enregistrement complet !",
                                     'trans_complete':">> Transcription complétée!",
                                     'api_error':"API non joignable.",
                                     'error_speech':"Audio non reconnu.",
                                     'idle_err1':"idle mode. Pas de command, ou commande non reconnue.",
                                     'idle_err2':"idle mode. Pas de voix détecté, ou audio non reconnu.",
                                     'idle_wake':"Commande reconnue: retour au mode actif.",
                                     'idle_exit':"Commande reconnue: fermeture du mode actif.",
                                     'text_sending':">> Envoie de la requête aux serveurs OpenAI."},
                              'commands':{'activated_pause':'Cortana Veille',
                                          'activated_exit':'Cortana Fermeture',
                                          'idle_exit':'Fermeture',
                                          'idle_start':'Activation',
                                          'prompt_image':"Générer image",
                                          'langchain_tools':"Prompt tools"},
                              'pronoun':'Moi',
                              'listening':"J'écoute...",
                              'protocol_terminated':'          ---- Protocole terminé ----',
                              }
                    }

idle_english = lambda key_start, key_end:print("============================================== \n"  \
                                               f"Idle state, say \'{key_start}\' to activate me...\n"  \
                                               f"Or, say \'{key_end}\' to deactivate me. \n" \
                                               "==============================================")
idle_french = lambda key_start, key_end:print("============================================== \n" \
                                              f"État de veille, dites \'{key_start}\' pour me réveiller...\n" \
                                              f"Ou dites \'{key_end}\' pour me désactiver.\n" \
                                              "==============================================\n")

def command_condition(text, command):
    if command.lower() in text.lower():
        return True
    else:
        return False

def text_command_detector(text, language):
    commands = predefined_answers[language]['commands']
    for command, text_command in commands.items():
        if command_condition(text, text_command):
            return command, text_command
        
    return None, None

