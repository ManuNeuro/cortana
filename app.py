# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 14:13:02 2023

@author: ManuMan
"""

import tkinter as tk
from tkinter import Text, font
from tkinter import *
from PIL import ImageTk
from PIL import Image,ImageTk
from cortana.model.cortana_class import button_voice, button_text
from cortana.model.cortana_class import cortana
import sys
import threading
import json
from tkhtmlview import HTMLLabel
from tkinter import messagebox as mbox
import contextlib
from io import StringIO
from markdown2 import Markdown
import numpy as np

# path = './results/log.md'
# with open(path, 'w') as f:
#     with contextlib.redirect_stdout(f):
#         print('#Hello, World')

class MarkdownOutput:
    def __init__(self, output_widget, filename):
        self.output_widget = output_widget
        self.buffer = StringIO()
        self.captured_output = ""
        self.filename = filename

    def write(self, text):
        self.buffer.write(text)
        self.captured_output += text
        self.update_widget()

    def update_widget(self):
        md2html = Markdown()
        output_text = self.buffer.getvalue()
        self.output_widget.config(state=tk.NORMAL)
        self.output_widget.delete("1.0", tk.END)
        self.output_widget.set_html('<div style="color: cyan">'+md2html.convert(output_text)+'</div>')
        self.output_widget.config(state=tk.DISABLED)
        self.save_to_markdown()
        
    def save_to_markdown(self):
        with open(f'results/{self.filename}.md', "w") as file:
            file.write(self.captured_output)
    
    def flush(self):
        self.buffer.flush()

# class RedirectedPrint:
#     def __init__(self, output_text):
#         self.output_text = output_text

#     def write(self, text):
#         self.output_text.insert(tk.END, text)
#         self.output_text.see(tk.END)

#     def flush(self):
#         pass

class MyApp:
    def __init__(self, root):
        # Set the window size
        self.root = root
        self.root.geometry("600x650")
        self.root.title("Cortana + chatGPT4")
        self.myfont = font.Font(family="Helvetica", size=14)
        self.rnd_tag = np.random.randint(1, 1000000, 1)[0]
        root.iconbitmap("icon.ico")
        
        # Set background image
        self.bg_image = ImageTk.PhotoImage(file="./images/cortana.png")
        bg_label = tk.Label(self.root, image=self.bg_image)
        bg_label.place(x=0, y=-70, relwidth=1, relheight=1)

        # Create a label for the entry widget
        entry_label_left = tk.Label(self.root, text="Enter your API key from openai:")
        entry_label_left.place(relx=0.1, rely=0.5)
        
        # Set entry
        self.entry = tk.Entry(root)
        self.entry.place(relx=0.4, rely=0.5)
        
        self.entry_prompt = tk.Text(self.root, width="1", font=self.myfont)
        self.entry_prompt.place(relx=0.4, rely=0.6, width=300, height=100)
        
        # Creating a photoimage object to use image
        photo=Image.open("./images/icon.png")
        
        
        # Resizing image to fit on button
        resized_img=photo.resize((30,30),Image.ANTIALIAS)
        icon=ImageTk.PhotoImage(resized_img)
        #Let us create a label for button event
        img_label= Label(image=icon)
        img_label.image = icon # keep a reference!
        # img_label.pack()
        
        # Create three buttons
        button1 = tk.Button(root, text="English", command=lambda:self.button_language('english', api_key=self.entry.get()))
        button2 = tk.Button(root, text="French", command=lambda:self.button_language('french', api_key=self.entry.get()))
        button3 = tk.Button(root, text="Send", command=lambda:self.button_chat(self.entry_prompt.get("1.0" , END)))
        button4 = tk.Button(root, text = 'Talk!', image=icon, command=lambda:self.button_talk())
        button4.pack()
        
        button1.place(relx=0.4, rely=0.1, anchor="center")
        button2.place(relx=0.55, rely=0.1, anchor="center")
        button3.place(relx=0.3, rely=0.65)
        button4.place(relx=0.2, rely=0.65)

        # Create a label for the entry widget (below)
        entry_label_below = tk.Label(root, text="API key is not stored and only use within a session")
        entry_label_below.place(relx=0.3, rely=0.55)
        
        
        # Create a label for the entry question
        entry_label_text = tk.Label(root, text="Enter you question here:")
        entry_label_text.place(relx=0.15, rely=0.6)
        
        self.outputbox = HTMLLabel(self.root, wrap=tk.WORD, width="1", background="Black", 
                                     html='<h1 style="color: cyan">Cortana</h1>') 
        self.outputbox.place(relx=0.5, rely=0.9, anchor="center", width=600, height=150)
        # self.outputbox.pack(fill=BOTH, expand=1, side=RIGHT)
        self.outputbox.fit_height()
        
        self.markdown_output = MarkdownOutput(self.outputbox, f'historic#{self.rnd_tag}')
        sys.stdout = self.markdown_output       
        
    def talk_with_cortana(self, **kwargs):
        self.my_cortana.talk_with_cortana(**kwargs)

    def chat_with_cortana(self, *args, **kwargs):
        self.my_cortana.submit_prompt(*args, **kwargs)
    
    def button_language(self, language, api_key):
        name = "gpt-4"
        language = 'english'
        api_key = None
        self.my_cortana = cortana(name, language, api_key=api_key)
        
    def button_talk(self):
        with open('./model/parameters.json') as json_file:
            kwargs = json.load(json_file)
            
        # Create a separate thread to run the on_button_click function
        threading.Thread(target=self.talk_with_cortana, kwargs=kwargs).start()
        
    def button_chat(self, input_text):
        with open('./model/parameters.json') as json_file:
            kwargs = json.load(json_file)
            
        # Create a separate thread to run the on_button_click function
        threading.Thread(target=self.chat_with_cortana, args=[input_text], kwargs=kwargs).start()
        self.entry_prompt.delete("1.0" , END)


root = tk.Tk()
app = MyApp(root)
root.mainloop()
