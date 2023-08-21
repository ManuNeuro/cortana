# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 08:48:47 2023

@author: ManuMan
"""
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import Text, font
from tkinter import *
from PIL import ImageTk
from PIL import Image,ImageTk
from ttkthemes import ThemedStyle
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
import subprocess as sp
programName = "C:\Program Files\MarkText\MarkText.exe"

# path = './results/log.md'
# with open(path, 'w') as f:
#     with contextlib.redirect_stdout(f):
#         print('#Hello, World')

class MarkdownOutput:
    def __init__(self, filename):
        self.captured_output = ""
        self.filepath = f'./results/{filename}.md'
        self.programpath = programName
        self.poll = 0
        
    def write(self, text):
        self.captured_output += text
        self.update_marktext()

    def update_marktext(self):
        self.save_to_markdown()
        self.launch_marketext()

    def launch_marketext(self):
        if self.poll == 0:
            p = sp.Popen([self.programpath, self.filepath])
            self.poll = p.poll()
        elif self.poll is None:
            pass
        
    def save_to_markdown(self):
        with open(self.filepath, "w") as file:
            file.write(self.captured_output)
    
    def flush(self):
        pass

class MyApp:
    def __init__(self, root):
        # Set the window size
        self.root = root
        self.root.geometry("650x640")
        self.root.title("Cortana + chatGPT4")
        self. root.configure(background = '#373e48')
        self.style = ThemedStyle(self.root)
        self.style.set_theme("blue")
        self.myfont = font.Font(family="Helvetica", size=14)
        self.def_filename()
        self.root.iconbitmap("icon.ico")
        
        # Set background image
        bg_image = Image.open("./images/cortana.png")
        resized_img=bg_image.resize((650,400),Image.LANCZOS)
        self.bg_image=ImageTk.PhotoImage(resized_img)
        bg_label = ttk.Label(self.root, image=self.bg_image)
        bg_label.grid(row = 1, column = 0, sticky = 'ne',)
        # bg_label.place(x=-70, y=-70, relwidth=1, relheight=1)

        # Create a label for the entry widget
        entry_label_left = ttk.Label(self.root, text="API key from openai:")
        entry_label_left.place(relx=0.5, rely=0.63)
        
        # Set entry
        self.entry = ttk.Entry(root)
        self.entry.place(relx=0.7, rely=0.63, width=150)
        
        self.entry_prompt = tk.Text(self.root, width="1", font=self.myfont)
        self.entry_prompt.place(relx=0.01, rely=0.66, width=635, height=175)
        
        # Creating icons
        photo=Image.open("./images/icon.png")
        # Resizing image to fit on button
        resized_img=photo.resize((30,30),Image.LANCZOS)
        icon=ImageTk.PhotoImage(resized_img)
        # Let us create a label for button event
        img_label= Label(image=icon)
        img_label.image = icon # keep a reference!

        photo=Image.open("./images/icon-open.png")
        # Resizing image to fit on button
        resized_img=photo.resize((30,30),Image.LANCZOS)
        icon2=ImageTk.PhotoImage(resized_img)
        # Let us create a label for button event
        img_label2= Label(image=icon2)
        img_label2.image = icon2 # keep a reference!
        
        photo=Image.open("./images/param.png")
        # Resizing image to fit on button
        resized_img=photo.resize((30,30),Image.LANCZOS)
        icon3=ImageTk.PhotoImage(resized_img)
        # Let us create a label for button event
        img_label3= Label(image=icon3)
        img_label3.image = icon3 # keep a reference!
        
        # Create a label for the entry question
        entry_label_text = ttk.Label(root, text="↓ Enter you question here ↓")
        entry_label_text.place(relx=0.01, rely=0.63)
        
        self.markdown_output = MarkdownOutput(self.filename)
        sys.stdout = self.markdown_output     
        
        # Create three buttons
        button1 = ttk.Button(root, text="En", command=lambda:self.button_language('english', api_key=self.entry.get()))
        button2 = ttk.Button(root, text="Fr", command=lambda:self.button_language('french', api_key=self.entry.get()))
        button3 = ttk.Button(root, text="Enter", width=100, 
                             command=lambda:self.button_chat(self.entry_prompt.get("1.0" , END)), )
        button4 = tk.Button(root, text = 'Talk!', image=icon, borderwidth=0, pady=0, padx=0,
                             command=lambda:self.button_talk())
        button5 = tk.Button(root, text = 'Open file', image=icon2, borderwidth=0, pady=0, padx=0,
                             command=lambda:sp.Popen([programName, f'./results/{self.filename}.md']))
        button6 = tk.Button(root, text = 'Parameters', image=icon3, borderwidth=0, pady=0, padx=0,
                             command=lambda:sp.Popen([self.open_param, self.param_path]))
        
        button1.place(relx=0.05, rely=0.05, anchor="center")
        button2.place(relx=0.12, rely=0.05, anchor="center")
        button3.place(relx=0.5, rely=0.96, anchor="center")
        button4.place(relx=0.92, rely=0.01)
        button5.place(relx=0.92, rely=0.08)
        button6.place(relx=0.92, rely=0.5)

    def def_filename(self):
        if not hasattr(self, "filename"):
            date = datetime.now()
            date_str = date.strftime('%Y-%m-%d')
            rnd_tag = np.random.randint(1, 1000000)
            self.filename = f'{date_str}_historic#{rnd_tag}'
            self.open_param = "C:\Program Files\Sublime Text 3\sublime_text.exe"
            self.param_path = "./model/parameters.json"
    
    def display_gif(self, filename):
        gif_path = "cortana-halo.gif"  # Replace with your GIF image path
        gif_image = Image.open('./images/{filename}.gif')
        self.gif_photo = ImageTk.PhotoImage(gif_image)
        gif_label = ttk.Label(self.root, image=self.gif_photo)

        
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
