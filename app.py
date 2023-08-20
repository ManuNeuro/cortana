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
import subprocess as sp
programName = "C:\Program Files\Sublime Text 3\sublime_text.exe"

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
        self.root.geometry("1200x650")
        self.root.title("Cortana + chatGPT4")
        self.root['background'] = "#000025"
        self.myfont = font.Font(family="Helvetica", size=14)
        self.def_filename()
        root.iconbitmap("icon.ico")
        
        # Set background image
        bg_image = Image.open("./images/cortana.png")
        resized_img=bg_image.resize((600,325),Image.ANTIALIAS)
        self.bg_image=ImageTk.PhotoImage(resized_img)
        bg_label = tk.Label(self.root, image=self.bg_image)
        bg_label.grid(row = 1, column = 0, sticky = 'ne',)
        # bg_label.place(x=-70, y=-70, relwidth=1, relheight=1)

        # Create a label for the entry widget
        entry_label_left = tk.Label(self.root, text="API key from openai:")
        entry_label_left.place(relx=0.01, rely=0.56)
        
        # Set entry
        self.entry = tk.Entry(root)
        self.entry.place(relx=0.11, rely=0.56, width=150)
        
        self.entry_prompt = tk.Text(self.root, width="1", font=self.myfont)
        self.entry_prompt.place(relx=0.01, rely=0.65, width=600, height=200)
        
        # Creating a photoimage object to use image
        photo=Image.open("./images/icon.png")
        # Resizing image to fit on button
        resized_img=photo.resize((30,30),Image.ANTIALIAS)
        icon=ImageTk.PhotoImage(resized_img)
        # Let us create a label for button event
        img_label= Label(image=icon)
        img_label.image = icon # keep a reference!

        photo=Image.open("./images/icon-open.png")
        # Resizing image to fit on button
        resized_img=photo.resize((30,30),Image.ANTIALIAS)
        icon2=ImageTk.PhotoImage(resized_img)
        # Let us create a label for button event
        img_label2= Label(image=icon2)
        img_label2.image = icon2 # keep a reference!
        
        # Create a label for the entry widget (below)
        # entry_label_below = tk.Label(root, text="API key is not stored and only use within a session")
        # entry_label_below.place(relx=0.3, rely=0.55)
        
        
        # Create a label for the entry question
        entry_label_text = tk.Label(root, text="Enter you question here:")
        entry_label_text.place(relx=0.01, rely=0.62)
        
        self.outputbox = HTMLLabel(self.root, wrap=tk.WORD, width="1", background="Black", 
                                     html='<h1 style="color: cyan">Cortana</h1>') 
        self.outputbox.place(relx=0.75, rely=0.48, anchor="center", width=580, height=640)
        # self.outputbox.pack(fill=BOTH, expand=1, side=RIGHT)
        # self.outputbox.fit_height()
        
        self.markdown_output = MarkdownOutput(self.outputbox, self.filename)
        sys.stdout = self.markdown_output     
        
        # Create three buttons
        button1 = tk.Button(root, text="En", command=lambda:self.button_language('english', api_key=self.entry.get()))
        button2 = tk.Button(root, text="Fr", command=lambda:self.button_language('french', api_key=self.entry.get()))
        print(self.filename)
        button3 = tk.Button(root, text="Enter", command=lambda:self.button_chat(self.entry_prompt.get("1.0" , END)))
        button4 = tk.Button(root, text = 'Talk!', image=icon, command=lambda:self.button_talk())
        button5 = tk.Button(root, text = 'Open file', image=icon2, command=lambda:sp.Popen([programName, f'./results/{self.filename}.md']))
        
        button1.place(relx=0.03, rely=0.05, anchor="center")
        button2.place(relx=0.05, rely=0.05, anchor="center")
        button3.place(relx=0.47, rely=0.9)
        button4.place(relx=0.46, rely=0.01)
        button5.place(relx=0.95, rely=0.03)
    
    def def_filename(self):
        if not hasattr(self, "filename"):
            rnd_tag = np.random.randint(1, 1000000)
            self.filename = f'historic#{rnd_tag}'
    
    def display_gif(self, filename):
        gif_path = "cortana-halo.gif"  # Replace with your GIF image path
        gif_image = Image.open('./images/{filename}.gif')
        self.gif_photo = ImageTk.PhotoImage(gif_image)
        gif_label = tk.Label(self.root, image=self.gif_photo)

        
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
