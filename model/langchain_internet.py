# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 17:31:25 2023

@author: ManuMan
"""

import os

from langchain.llms import OpenAI
from langchain.agents import load_tools
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chains.conversation.memory import ConversationSummaryBufferMemory

from datetime import datetime, timezone

currentDateAndTime = datetime.now(timezone.utc)

from langchain.chat_models import ChatOpenAI

def test_model():
    # gpt-4 gpt-3.5-turbo gpt-4-0314
    # llm = ChatOpenAI(model_name='text-davinci-003', temperature=0.9)
    # llm = ChatOpenAI(model_name='gpt-3.5-turbo-0613', temperature=0.1, max_tokens=4097 // 8)
    # llm = ChatOpenAI(model_name='gpt-3.5-turbo-16k-0613', temperature=0.1, max_tokens=4097 // 8)
    llm = ChatOpenAI(model_name='gpt-4', temperature=0.1, max_tokens=4097 // 8)

    # tools = load_tools(['llm-math'], llm=gpt3)+ [ddgtool]
    # tools = load_tools(['serpapi', 'llm-math'], llm=gpt3)
    # tools = load_tools(['serpapi', 'python_repl'], llm=gpt3)
    # tools = load_tools(['serpapi'], llm=gpt3)
    # agent = initialize_agent(tools , llm=llm, agent=AgentType.SELF_ASK_WITH_SEARCH, verbose=True)
    # tools = load_tools(["ddg-search", "python_repl"], llm=llm)
    # tools = load_tools(["ddg-search", "news-api", "pal-math"], llm=llm)
    # tools = load_tools(["ddg-search", "pal-math"], llm=llm)

    memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=1024, memory_key="chat_history")

    # tools = load_tools(["ddg-search"], llm=llm)

    # AgentType.ZERO_SHOT_REACT_DESCRIPTION, SELF_ASK_WITH_SEARCH
    # agent = initialize_agent(tools , llm=llm, agent='zero-shot-react-description', verbose=True)
    # agent = initialize_agent(tools, llm=llm, agent='conversational-react-description', verbose=True)
    # agent.run("Is btc going to go up in 12h if you compare with other coins and their recent history?")
    prompt = "Name one coin that will rise and another that will go down in the next 1h, having a look at Twitter. " \
             f"Make sure you're using up to date data, now it's {currentDateAndTime} UTC. Give an argument for your choice." \
             "Look at the prices movements and use technical analysis and Twitter info."

    prompt = "Make a justified prediction about BTC: is it going up or down in the next hour. " \
             f"Make sure you're using up to date data, now it's {currentDateAndTime} UTC. " \
             f"Give an argument for your choice, be specific about the data you gathered. " \
             f"For example show at least four tweets that you used to make the decision. " \
             f"Provide a statistical analysis about the price variation. " \
             "Use technical analysis on the prices movements and combine that information with what you gathered on Twitter. " \
             "After the justification, the last word you say has to be Buy if you think it's going up, Sell if you think it's going down, or " \
             "Wait if no action is necessary, any of the three followed by a period. " \
             "I'll use that to make the final decision in a trading bot. " \
             "Make sure that your last reply is consistent with everything I asked you in this prompt." \
             "If you need data on the prices, don't try to read csvs but parse the prices from a website instead. " \
             "You can use the search engine or the LLM to do the analysis."

    prompt = 'What is the email adress of Anima Anandkumar?'

    # 'The countries we consider are Canada, France, Italy, Spain, Germany, Estonia, Portugal. ' \
    prompt = 'Create an table to determine which country is the best to register a company for crypto trading. ' \
             'The countries we consider are Canada, France. ' \
             'We want a row for each country, and a column for each of the following: ' \
             'Price of registering a company, if residency is required, what are the taxes on profit, ' \
             'how long we need to wait to get the company registered, and a column with the references to the sources. ' \
             'At the end of your reasoning, you have to provide the table as the output with the information you found ' \
             'organized properly. Fill the columns with the information you have gathered, exact prices, exact ' \
             'taxes, and so on. Be thorough and complete all the columns, keep searching until you have all the info.'

    prompt = 'Elaborate this intro to the preliminaries of a thesis, and triple its length. Make it sound more academic. ' \
             'Update it with info you could find online.' \
             'The earliest form of the stability analysis in the study of neural networks is often attributed ' \
             'to \cite{hochreiter1991untersuchungen} who identified that the tendency of gradients to compose ' \
             'exponentially with time was behind the difficulty of training early forms of recurrent neural networks. ' \
             'The authors of \cite{bengio1994learning} notice that the difficulty stems from the fact that most initializations lead to explosion and vanishing of the gradients. Restating their finding differently, there are infinitely many locally unstable initializations, and only one stable one, in a sense that can be made rigorous. In response,  several techniques have been designed to stabilize gradients, such as Batch and Layer Normalization, gradient clipping, gating mechanisms and skip connections \cite{ioffe2015batch, ba2016layer, zhanggradient, hochreiter1997long, he2016deep}, that have prepared the path for the great successes of learning algorithms. One well known stabilization technique is to find mathematically the set of hyper-parameters required by a given architecture to avoid a gradient explosion at initialization, where the best-known examples are arguably Glorot and He initializations \cite{glorot2010understanding,he2015delving}. '

    # tools = [tot_tool(prompt)]
    # tools = load_tools(["ddg-search"], llm=llm) +  [tot_tool(prompt)]
    tools = load_tools(["ddg-search"], llm=llm)

    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True, memory=memory,
                             # max_iterations=10,
                             min_iterations=8)
    print(prompt)
    output = agent.run(prompt)
    print('output', output)