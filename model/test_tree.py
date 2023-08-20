# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 20:17:45 2023

@author: ManuMan
"""
import numpy as np
from cortana_class import cortana

def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)


# Tree of thougts
def get_Ptrue(cortana):
    string = my_cortana.last_answer
    if has_numbers(string):
        string = my_cortana.last_answer.split('P_true')[-1]
        if '=' in string:   
            string = string.split('=')[1]
        string = string.split(' ')[1]
        if '%' in string:
            string = string.split('%')[0]
        elif '.' in string:
            string = string.split('.')[0]
        P_true = int(string)
        return P_true
    else:
        return 50

generate_new_thought = lambda index: f'Complete the following series of thougts T of given index'\
                            f'T:{index}, make sure to not modify it, just add new'\
                            'thougts after this one, while trying to answer the initial question Q:'
chain_of_thought = lambda prompt: f"Q: {prompt}\n"\
                                "A: Let's think step by step.To provide a solution to the problem at hand. I will provide all calculus required to arrive at my conclusion "\
                                "Each thought must be marked by a T#:, with with # the index number, and each though should end with a dot: .\n"

def get_thougts(my_cortana):
    condition_stop = False
    index = 1
    thougts = []
    cortana_answer = my_cortana.last_answer
    buffer_thoughts = cortana_answer.split(f'T{index}:')[1]
    while not condition_stop:
        index += 1 
        if len(buffer_thoughts.split(f'T{index}:')) > 1:
            thougts.append(buffer_thoughts.split(f'T{index}:')[0])
            buffer_thoughts = buffer_thoughts.split(f'T{index}:')[1]
        else:
            thougts.append(buffer_thoughts)
            condition_stop = True
    return thougts

input_prompt = 'Imagine I own 0.5 g of gold, and assume that the price of gold is 32000USD as of now. Second, assume that the next year price is'\
    '35000: should I buy, wait, or sell ? Just assume what I say is absolutely right with 100% cetainty.'

train_of_thougt_input = "Taking all given information "\
                f"into account, and assuming all statements in the first query as true."\
                " Assuming as well as true, the current chain of thought T# of corresponding index given a list format [1, 2, ..., n]. Verify that the last thought index n is true"\
                f"Your output should explicitly provide a percentage with following format, \'P_true = X%\' "\
                "\between 0 and 100. This percentage evalaute, according to your knolwedge, the probability "\
                "that the statement is correct, with 0 being 0 chance it is correct. 50% meaning, not knowing "\
                "or half, and 100% this statement is true"

iterative_prompt = lambda index: "Taking all previous information "\
                f"into account. Assuming chain of T: {np.arange(1, index+1)}. "\
                "Verify that the last thought is true: {index}"\
       
my_cortana = cortana("gpt-3.5-turbo", 'french') 
my_cortana.reset_messages(train_of_thougt_input)
initial_prompt = chain_of_thought(input_prompt)
number_of_trials = 10
P_thresh = 49
max_tokens = 400
temperature = 0.5

for trial in range(number_of_trials):
    print(f'----- Root {trial} -----')
    my_cortana.prompt(initial_prompt, max_tokens=max_tokens, temperature=temperature, _print=False)
    thougts = get_thougts(my_cortana)
    init_thougts = thougts
    P_true = 100
    index = 0
    while index < len(thougts):
        print(f'----- Thougt {index} -----')
        print(thougts[index])
        thought_to_evaluate = iterative_prompt(index)
        my_cortana.prompt(thought_to_evaluate, max_tokens=max_tokens, _print=False)
        P_true = get_Ptrue(my_cortana)
        
        print(f'P_true = {P_true}')
        if P_true > P_thresh:
            index += 1
        elif (P_true <= P_thresh) and index > 1:
            new_prompt = generate_new_thought(index-1)
            my_cortana.prompt(new_prompt, max_tokens=max_tokens, temperature=temperature, _print=False)
            thougts = get_thougts(my_cortana)
            print('-> Generating new thougts')
        elif P_true <= P_thresh:
            print('-> Next branch')
            break
    else:
        break
print('===========================')
print(thougts[-1])
messages = my_cortana.messages
# my_cortana.prompt_image('A cat in a swiming pool')