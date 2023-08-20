# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 14:27:08 2023

@author: ManuMan
"""

from cortana.model.cortana_class import cortana

def main(name, language, api_key, **kwargs):
    my_cortana = cortana(language=language, api_key=api_key) 
    my_cortana.set_model(name)
    
    condition = True
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
    print('Welcome in the interactive chat with Cortana\n')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n')
    while condition is True:
        print('Your prompt:\n')
        input_text = input()
        condition = my_cortana.submit_prompt(input_text, **kwargs)

if __name__ == '__main__':
    name = "gpt-4"
    language = 'english'
    api_key = None
    kwargs = {'image':dict(n=5, 
                           size="1024x1024"),
              'text':dict(max_tokens=700, 
                         temperature=0.4),
              }
    main(name, language, api_key, **kwargs)