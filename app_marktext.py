# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 08:48:47 2023

@author: ManuMan
"""
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import Text, font
from tkinter import *
from PIL import Image,ImageTk, ImageSequence
from ttkthemes import ThemedStyle
from cortana.model.cortana_class import cortana
import sys
import threading
import json
import numpy as np
import subprocess as sp
from win32api import GetSystemMetrics
from itertools import count

programName = "C:\Program Files\MarkText\MarkText.exe"

# path = './results/log.md'
# with open(path, 'w') as f:
#     with contextlib.redirect_stdout(f):
#         print('#Hello, World')

def window_size_str():
    return str(int(GetSystemMetrics(0)/2)) + 'x' + str(GetSystemMetrics(1)-50)

def resize_gif(filename, size):
    
    # Open source
    im = Image.open(f"./images/{filename}.gif")
    
    # Get sequence iterator
    frames = ImageSequence.Iterator(im)
    
    # Wrap on-the-fly thumbnail generator
    def thumbnails(frames):
        for frame in frames:
            thumbnail = frame.copy()
            thumbnail.thumbnail(size, Image.LANCZOS)
            yield thumbnail
    frames = thumbnails(frames)

    # Save output
    om = next(frames) # Handle first frame separately
    om.info = im.info # Copy sequence info
    om.save(f"./images/{filename}_resized.gif", 
            save_all=True, append_images=list(frames))
class ImageLabel(tk.Label):
    
    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        self.loc = 0
        self.frames = []

        try:
            for i in count(1):
                self.frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass

        try:
            self.delay = int(im.info['duration'] * 1.6)
        except:
            self.delay = 100

        if len(self.frames) == 1:
            self.config(image=self.frames[0])
        else:
            self.next_frame()

    def unload(self):
        self.config(image="")
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.loc += 1
            self.loc %= len(self.frames)
            self.config(image=self.frames[self.loc])
            self.after(self.delay, self.next_frame)

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

class MyApp(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.root.geometry(window_size_str())
        self.root.title("Cortana + chatGPT4")
        self.root.configure(background = '#373e48')
        self.style = ThemedStyle(self.root)
        self.style.set_theme("breeze")
        self.myfont = font.Font(family="Helvetica", size=14)
        self.def_filename()
        self.root.iconbitmap("icon.ico")
        
        # Create a label for the entry widget
        entry_label_left = ttk.Label(self.root, text="API key from openai:")
        entry_label_left.place(relx=0.5, rely=0.62)
        
        # Set entry
        self.entry = ttk.Entry(root)
        self.entry.place(relx=0.7, rely=0.605, width=150)
        
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
        
        photo=Image.open("./images/folder.png")
        # Resizing image to fit on button
        resized_img=photo.resize((30,30),Image.LANCZOS)
        icon4=ImageTk.PhotoImage(resized_img)
        # Let us create a label for button event
        img_label4= Label(image=icon4)
        img_label4.image = icon4 # keep a reference!
        
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
        button4 = tk.Button(root, text = 'Talk!', image=icon, borderwidth=0, pady=0, padx=0, background="black", 
                             command=lambda:self.button_talk())
        button5 = tk.Button(root, text = 'Open file', image=icon2, borderwidth=0, pady=0, padx=0, background="white",
                             command=lambda:sp.Popen([programName, f'./results/{self.filename}.md']))
        button6 = tk.Button(root, text = 'Parameters', image=icon3, borderwidth=0, pady=0, padx=0, background="white",
                             command=lambda:sp.Popen([self.open_param, self.param_path]))
        button7 = tk.Button(root, text = 'Folder', image=icon4, borderwidth=0, pady=0, padx=0, background="black",
                             command=lambda:os.startfile(self.folder_res))
        
        
        button1.place(relx=0.1, rely=0.05, anchor="center")
        button2.place(relx=0.1, rely=0.1, anchor="center")
        button3.place(relx=0.5, rely=0.96, anchor="center")
        button4.place(relx=0.92, rely=0.01)
        button5.place(relx=0.92, rely=0.08)
        button6.place(relx=0.92, rely=0.5)
        button7.place(relx=0.05, rely=0.5)
    
    @staticmethod
    def monitor_size(x_ratio, y_ratio):
        return int(GetSystemMetrics(0)*x_ratio), int(GetSystemMetrics(1)*y_ratio)
        
    def def_filename(self):
        if not hasattr(self, "filename"):
            date = datetime.now()
            date_str = date.strftime('%Y-%m-%d')
            rnd_tag = np.random.randint(1, 1000000)
            self.filename = f'{date_str}_historic#{rnd_tag}'
            self.open_param = "C:\Program Files\Sublime Text 3\sublime_text.exe"
            self.param_path = "./model/parameters.json"
            self.folder_res = path = os.path.realpath('./results/')
            
            # Set background image
            bg_image = Image.open("./images/cover2.jpg")
            resized_img=bg_image.resize(self.monitor_size(0.5, 0.55), Image.LANCZOS)
            self.bg_image=ImageTk.PhotoImage(resized_img)
            bg_label = ttk.Label(self.root, image=self.bg_image)
            bg_label.grid(row = 0, column = 0, sticky = 'ne',)
            bg_label.place(relx=0, rely=0)
            
            self.create_widgets('cortana_opening')
            
    def talk_with_cortana(self, **kwargs):
        self.my_cortana.talk_with_cortana(**kwargs)

    def chat_with_cortana(self, *args, **kwargs):
        self.my_cortana.submit_prompt(*args, **kwargs)
    
    def button_language(self, language, api_key):
        name = "gpt-4"
        api_key = None
        self.my_cortana = cortana(name, language, api_key=api_key)
        self.gif.unload()
        # self.create_widgets('cortana-halo')
        
        
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
    
    def create_widgets(self, filename):
        resize_gif(filename, self.monitor_size(0.5, 0.55))
        filepath = f"./images/{filename}_resized.gif"
        # label_gif = ttk.Label(self.root)
        self.gif = ImageLabel(self.root)
        self.gif.load(filepath)       
        self.gif.place(relx=0.2, rely=0.005)
        self.launch_gif()

    def launch_gif(self):
        threading.Thread(target=self.gif.next_frame()).start()

root = tk.Tk()
app = MyApp(root)
root.mainloop()
