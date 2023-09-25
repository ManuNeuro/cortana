# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 15:41:52 2023

@author: ManuMan
"""

# %% Simple query

from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain


# Step 3: Get user input
user_input = input("Enter a concept: ")
 
# Step 4: Define the Prompt Template
prompt = PromptTemplate(
    input_variables=["concept"],
    template="Define {concept} with a real-world example?",
)
 
# Step 5: Print the Prompt Template
print(prompt.format(concept=user_input))
 
# Step 6: Instantiate the LLMChain
llm = OpenAI(temperature=0.9)
chain = LLMChain(llm=llm, prompt=prompt)
 
# Step 7: Run the LLMChain
output = chain.run(user_input)
print(output)
    

# %% Turorial: conversation memory   
# https://www.pinecone.io/learn/series/langchain/langchain-conversational-memory/

basedir_model = os.path.dirname(__file__)

from cortana.api.encrypt import decrypt_key
path_key = basedir_model.split('model')[0] + 'api\\'
os.environ["OPENAI_API_KEY"] = decrypt_key(path_key, 'encrypted_key')    

from langchain import OpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory


# first initialize the large language model
llm = OpenAI(
	temperature=0,
	model_name="text-davinci-003"
)

# now initialize the conversation chain
conversation = ConversationChain(llm=llm)
print(conversation("Good morning AI!"))

conversation_buf = ConversationChain(
    llm=llm,
    memory=ConversationBufferMemory()
)
print(conversation_buf("Good morning AI!"))

# %% Counting the number of tokens

from langchain.callbacks import get_openai_callback

def count_tokens(chain, query):
    with get_openai_callback() as cb:
        result = chain.run(query)
        print(f'Spent a total of {cb.total_tokens} tokens')

    return result

count_tokens(
    conversation_buf, 
    "My interest here is to explore the potential of integrating Large Language Models with external knowledge"
)

# %% Check the memory 

print(conversation_buf.memory.buffer)

# %% ConversationSummaryMemory

from langchain.chains.conversation.memory import ConversationSummaryMemory

conversation_sum = ConversationChain(
	llm=llm,
	memory=ConversationSummaryMemory(llm=llm)
)

print(conversation_sum.memory.prompt.template)

# %% without count_tokens we'd call `conversation_sum("Good morning AI!")`
# but let's keep track of our tokens:
    
count_tokens(
    conversation_sum, 
    "Good morning AI!"
)


count_tokens(
    conversation_sum, 
    "My interest here is to explore the potential of integrating Large Language Models with external knowledge"
)


count_tokens(
    conversation_sum, 
    "I just want to analyze the different possibilities. What can you think of?"
)


print(conversation_sum.memory.buffer)

# %% ConversationBufferWindowMemory

from langchain.chains.conversation.memory import ConversationBufferWindowMemory

conversation_bufw = ConversationChain(
	llm=llm,
	memory=ConversationBufferWindowMemory(k=2)
)

count_tokens(
    conversation_bufw, 
    "Good morning AI!"
)

count_tokens(
    conversation_bufw, 
    "My interest here is to explore the potential of integrating Large Language Models with external knowledge"
)

count_tokens(
    conversation_bufw, 
    "I just want to analyze the different possibilities. What can you think of?"
)


count_tokens(
    conversation_bufw, 
    "Which data source types could be used to give context to the model?"
)


count_tokens(
    conversation_bufw, 
    "What is my aim again?"
)


bufw_history = conversation_bufw.memory.load_memory_variables(
    inputs=[]
)['history']

print(bufw_history)

# %% ConversationSummaryBufferMemory
from langchain.prompts import PromptTemplate

from langchain.chains.conversation.memory import ConversationSummaryBufferMemory

conversation_sum_bufw = ConversationChain(
    llm=llm, memory=ConversationSummaryBufferMemory(
        llm=llm,
        max_token_limit=3000
        )
    )

count_tokens(
    conversation_sum_bufw, 
    "Good morning AI! Do you feel well ?"
)

count_tokens(
    conversation_sum_bufw, 
    "My interest here is to explore the potential of integrating Large Language Models with external knowledge"
)

count_tokens(
    conversation_sum_bufw, 
    "I just want to analyze the different possibilities. What can you think of?"
)


count_tokens(
    conversation_sum_bufw, 
    "Which data source types could be used to give context to the model?"
)


count_tokens(
    conversation_sum_bufw, 
    "What is my aim again?"
)

bufw_history = conversation_sum_bufw.memory.load_memory_variables(
    inputs=[]
)['history']

print(bufw_history)

# %% PromptTemplate

from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessage, HumanMessagePromptTemplate

template = ChatPromptTemplate.from_messages([
    {"system": "You are a helpful AI bot. Your name is {name}."},
    {"human": "Hello, how are you doing?"},
    {"ai": "I'm doing well, thanks!"},
    {"human": "{user_input}"},]
)

messages = template.format_messages(
    name="Bob",
    user_input="What is your name?"
)

count_tokens(
    conversation_sum_bufw, 
    messages,
)


# %% Clear memory

conversation_sum_bufw.memory.clear()

bufw_history = conversation_sum_bufw.memory.load_memory_variables(
    inputs=[]
)['history']

print(bufw_history)

count_tokens(
    conversation_sum_bufw, 
    "What was my last question?"
)