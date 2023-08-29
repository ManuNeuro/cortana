# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 08:48:47 2023

@author: ManuMan
"""
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import Text, font, filedialog
from tkinter import *
from PIL import Image,ImageTk, ImageSequence
from ttkthemes import ThemedStyle
from cortana.model.cortana_class import cortana
from cortana.api.encrypt import encrypt_key, decrypt_key
# from cortana.model.buttons import ButtonApp
import sys
import threading
import json
import numpy as np
import subprocess as sp
from win32api import GetSystemMetrics
from itertools import count
import gc
import weakref
import signal 

basedir = os.path.dirname(__file__)

with open('./model/parameters.json') as json_file:
    kwargs = json.load(json_file)
    
programName = kwargs['app']['programName']
openParam = kwargs['app']['openParam']

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = "dorean.cortana.gpt4.0.1"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

def create_icon(filename, icon_sizes = [(64,64)]):
    img = Image.open(f"./images/{filename}.png")
    img.save('icon.ico', sizes=icon_sizes)

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

def load_markdown_file(filename):
    with open(filename, 'r') as file:
        content = file.read()
    return content

class MarkdownOutput:
    def __init__(self, filename, captured_output=""):
        self.captured_output = captured_output
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
            self.process = sp.Popen([self.programpath, self.filepath])
            self.poll = self.process.poll()
        elif self.poll is None:
            pass
        
    def save_to_markdown(self):
        with open(self.filepath, "w") as file:
            file.write(self.captured_output)
    
    def flush(self):
        pass
    
def create_icon(filename):
    photo=Image.open(f"./images/{filename}")
    # Resizing image to fit on button
    resized_img=photo.resize((30,30),Image.LANCZOS)
    icon=ImageTk.PhotoImage(resized_img)
    # Let us create a label for button event
    img_label= Label(image=icon)
    img_label.image = icon # keep a reference!
    return img_label
    
class CortanaApp(tk.Frame):
    def __init__(self, root):
        super().__init__()
        self.root = root
        
        self.root.geometry(window_size_str())
        self.root.title("Cortana + chatGPT4")
        self.root.configure(background = "#13273a")
        self.style = ThemedStyle(self.root)
        self.style.set_theme("breeze")
        self.myfont = font.Font(family="Helvetica", size=14)
        self.root.iconbitmap("icon.ico")
        
        # Initialization the app
        self.def_load()
        
        # Launching app buttons
        self.launching_app()
        
        # Interactive text box to chat with cortana
        self.entry_prompt = tk.Text(self.root, width="1", font=self.myfont)
        self.entry_prompt.place(relx=0.01, rely=0.66, width=635, height=175)
        
        entry_label_text = ttk.Label(self.root, text="↓ Enter your question here ↓")
        entry_label_text.place(relx=0.01, rely=0.63)

        # Rerouting all output to markdown file        
        self.markdown_output = MarkdownOutput(self.filename)
        sys.stdout = self.markdown_output     

    @staticmethod
    def monitor_size(x_ratio, y_ratio):
        return int(GetSystemMetrics(0)*x_ratio), int(GetSystemMetrics(1)*y_ratio)
    
    def new_filename(self):       
        date = datetime.now()
        date_str = date.strftime('%Y-%m-%d')
        rnd_tag = np.random.randint(1, 1000000)
        filename = f'{date_str}_historic#{rnd_tag}' 
        if hasattr(self, 'filename'): # If this is not the first time
            self.markdown_output = MarkdownOutput(filename)
            sys.stdout = self.markdown_output
        self.filename = filename
    
    def load_from_file(self):
        filename = filedialog.askopenfilename(initialdir="./results/")
        last_messages = load_markdown_file(filename)
        self.filename = os.path.basename(filename).split('.md')[0]
        self.my_cortana.messages.append({'role':'user', "content":last_messages})
        sp.Popen([programName, f'./results/{self.filename}.md'])
        self.markdown_output = MarkdownOutput(self.filename, last_messages)
        sys.stdout = self.markdown_output
        
    def def_load(self):
        if not hasattr(self, "filename"):
            self.new_filename()
            self.open_param = openParam
            self.param_path = "./model/parameters.json"
            self.folder_res = path = os.path.realpath('./results/')
            
            # Set background image
            bg_image = Image.open("./images/cover1.jpg")
            resized_img=bg_image.resize(self.monitor_size(0.5, 0.55), Image.LANCZOS)
            self.bg_image=ImageTk.PhotoImage(resized_img)
            self.bg_label = ttk.Label(self.root, image=self.bg_image)
            self.bg_label.grid(row = 0, column = 0, sticky = 'ne',)
            self.bg_label.place(relx=0, rely=0)
            
            self.create_widgets_gif('cortana_opening')

    def create_widgets_gif(self, filename):
        resize_gif(filename, self.monitor_size(0.5, 0.55))
        filepath = f"./images/{filename}_resized.gif"
        # label_gif = ttk.Label(self.root)
        self.gif = ImageLabel(self.root)
        self.gif.load(filepath)       
        self.gif.place(relx=0.2, rely=0.005)
        self.launch_gif()
    
    def launch_gif(self):
        threading.Thread(target=self.gif.next_frame()).start()
    
          
    def talk_with_cortana(self, **kwargs):
        self.my_cortana.talk_with_cortana(**kwargs)
        
    def chat_with_cortana(self, *args, **kwargs):
        self.my_cortana.submit_prompt(*args, _voice=False, **kwargs)
        '''
        In theory the following code should kill the app and launch it again as
        soon as the answer is generated, but this won't work if there are
        multiple tabs open in marktext. 
        
        At the end of the day, I prefer to have to do the refresh manually than
        the app having to load over and over each time there is an answer.
        
        Add this code if you want the "auto-reload":
        
        self.markdown_output.process.terminate()
        self.markdown_output.process = sp.Popen([self.markdown_output.programpath, 
                                                  self.markdown_output.filepath])
        '''
                      
    def start_talk(self):
        with open('./model/parameters.json') as json_file:
            kwargs = json.load(json_file)
            
        # Create a separate thread to run the on_button_click function
        self.my_cortana.flag = True
        threading.Thread(target=self.talk_with_cortana, kwargs=kwargs).start()
        
    def start_chat(self, input_text):
        with open('./model/parameters.json') as json_file:
            kwargs = json.load(json_file)
            
        # Create a separate thread to run the on_button_click function
        threading.Thread(target=self.chat_with_cortana, args=[input_text], kwargs=kwargs).start()
        self.entry_prompt.delete("1.0" , END)
    
    def launching_app(self):
        self.button_language()
        self.button_parameter()  

    def button_language(self):
        self.lang_label = tk.Label(self.root, text="Select language!")
        self.lang_label.place(relx=0.1, rely=0.17, anchor="center")
        self.button_fr = ttk.Button(self.root, text="En", command=lambda:self.launch_cortana('english', api_key=self.get_api_key()))
        self.button_en = ttk.Button(self.root, text="Fr", command=lambda:self.launch_cortana('french', api_key=self.get_api_key()))
        self.button_fr.place(relx=0.1, rely=0.05, anchor="center")
        self.button_en.place(relx=0.1, rely=0.1, anchor="center")
    
    def button_parameter(self):
        self.param_label = tk.Label(self.root, text="Provide path to markdown editor!")
        self.param_label.place(relx=0.65, rely=0.624, anchor="center")
        if not hasattr(self, "img_param"):
            self.img_param = create_icon("param.png")
        self.button_param = tk.Button(self.root, text = 'Parameters', image=self.img_param.image, borderwidth=0, pady=0, padx=0, background="#13273a",
                                      command=lambda:sp.Popen([self.open_param, self.param_path]))
        self.button_param.place(relx=0.825, rely=0.601)
    
    def regular_app_button(self):
        self.lang_label.place_forget()
        self.param_label.place_forget()

        if not hasattr(self, "img_talk"):
            self.img_talk = create_icon("icon1.png")
        
        if not hasattr(self, "img_open"):
            self.img_open = create_icon("icon-open.png")
        
        if not hasattr(self, "img_folder"):
            self.img_folder = create_icon("folder.png")

        if not hasattr(self, "img_plus"):
            self.img_plus = create_icon("plus.png")
    
        if not hasattr(self, "img_load"):
            self.img_load = create_icon("load.png")
            
        if not hasattr(self, "img_preprompt"):
            self.img_preprompt = create_icon("preprompt.png")
            
        self.button_enter = ttk.Button(self.root, text="Enter", width=100, 
                             command=lambda:self.start_chat(self.entry_prompt.get("1.0" , END)), )
        self.button_talk = tk.Button(self.root, text = 'Talk!', image=self.img_talk.image, borderwidth=0, pady=0, padx=0, background="#13273a", 
                             command=lambda:self.start_talk())
        self.button_file = ttk.Button(self.root, text = 'Open file', image=self.img_open.image, #borderwidth=0, pady=0, padx=0, background="white",
                             command=lambda:sp.Popen([programName, f'./results/{self.filename}.md']))
        self.button_folder = tk.Button(self.root, text = 'Folder', image=self.img_folder.image, borderwidth=0, pady=0, padx=0, background="#13273a",
                             command=lambda:os.startfile(self.folder_res))
        self.button_new = tk.Button(self.root, text = 'New', image=self.img_plus.image, borderwidth=0, pady=0, padx=0, background="#13273a",
                            command=lambda:self.new_filename())
        self.button_load = ttk.Button(self.root, text = 'Load', image=self.img_load.image, #borderwidth=0, pady=0, padx=0, background="#13273a",
                            command=lambda:self.load_from_file())
        self.button_preprompt = ttk.Button(self.root, text = 'PePrompt', image=self.img_preprompt.image, #borderwidth=0, pady=0, padx=0, background="#13273a",
                              command=lambda:sp.Popen([self.open_param, './model/preprompt.json']))
        self.button_enter.place(relx=0.5, rely=0.96, anchor="center")
        self.button_talk.place(relx=0.935, rely=0.601)
        self.button_file.place(relx=0.905, rely=0.025)
        self.button_folder.place(relx=0.88, rely=0.601)
        self.button_new.place(relx=0.77, rely=0.601)
        self.button_load.place(relx=0.905, rely=0.1)
        self.button_preprompt.place(relx=0.03, rely=0.51)
        self.create_button_api()
    
    def create_button_api(self):
        if not hasattr(self, "img_api"):
            self.img_api = create_icon("api.png")
        
        self.button_api = ttk.Button(self.root, text = 'api', image=self.img_api.image, #borderwidth=0, pady=0, padx=0, background="#13273a",
                              command=lambda:self.create_apikey())
        self.button_api.place(relx=0.03, rely=0.42)
        
    def create_apikey(self):
        self.button_api.place_forget()
        self.api_label = tk.Label(self.root, text="Enter API key from OpenAi")
        self.api_label.pack(pady=15, anchor=tk.CENTER)
        self.api_entry = tk.Entry(self.root)
        self.api_entry.pack(ipadx=60, pady=10, anchor=tk.CENTER)#ipadx=40, padx=35, pady=160, anchor='sw')
        self.button_ok = tk.Button(self.root, text="OK", command=self.remove_entry)
        self.button_ok.pack(pady=10, anchor=tk.CENTER)#padx=150, pady=160, anchor='w')
        
    def remove_entry(self):
        self.api_key = self.api_entry.get()
        encrypt_key(self.api_key, path='./api/')
        self.api_label.pack_forget()
        self.api_entry.pack_forget()
        self.button_ok.pack_forget()
        self.create_button_api()

    def launch_cortana(self, language, api_key):
        name = "gpt-4"
        api_key = None
        self.my_cortana = cortana(name, language, api_key=api_key)
        self.gif.unload()
        self.regular_app_button()
    
    def get_api_key(self):
        try:
            self.api_key = decrypt_key(path='./api/')
        except:
            self.create_apikey()
            self.api_key = decrypt_key(path='./api/')
        return self.api_key
    
    def launching_app(self):
        self.button_language()
        self.button_parameter()  

    def button_language(self):
        self.lang_label = tk.Label(self.root, text="Select language!")
        self.lang_label.place(relx=0.1, rely=0.17, anchor="center")
        self.button_fr = ttk.Button(self.root, text="En", command=lambda:self.launch_cortana('english', api_key=self.get_api_key()))
        self.button_en = ttk.Button(self.root, text="Fr", command=lambda:self.launch_cortana('french', api_key=self.get_api_key()))
        self.button_fr.place(relx=0.1, rely=0.05, anchor="center")
        self.button_en.place(relx=0.1, rely=0.1, anchor="center")
    
    def button_parameter(self):
        self.param_label = tk.Label(self.root, text="Provide path to markdown editor!")
        self.param_label.place(relx=0.65, rely=0.624, anchor="center")
        if not hasattr(self, "img_param"):
            self.img_param = create_icon("param.png")
        self.button_param = tk.Button(self.root, text = 'Parameters', image=self.img_param.image, borderwidth=0, pady=0, padx=0, background="#13273a",
                                      command=lambda:sp.Popen([self.open_param, self.param_path]))
        self.button_param.place(relx=0.825, rely=0.601)
    
    def buttons_regular(self):
        self.button_fr = ttk.Button(self.root, text="En", command=lambda:self.regular_cortana('english', api_key=self.get_api_key()))
        self.button_en = ttk.Button(self.root, text="Fr", command=lambda:self.regular_cortana('french', api_key=self.get_api_key()))
        self.button_fr.place(relx=0.1, rely=0.05, anchor="center")
        self.button_en.place(relx=0.1, rely=0.1, anchor="center")
        self.button_param = tk.Button(self.root, text = 'Parameters', image=self.img_param.image, borderwidth=0, pady=0, padx=0, background="#13273a",
                                      command=lambda:sp.Popen([self.open_param, self.param_path]))
        self.button_param.place(relx=0.825, rely=0.601)
        self.regular_app_button()
        
    def active_mode(self):
        # Set background image
        bg_image = Image.open("./images/cover-rec.png")
        resized_img=bg_image.resize(self.monitor_size(0.5, 0.55), Image.LANCZOS)
        self.bg_image=ImageTk.PhotoImage(resized_img)
        self.bg_label = ttk.Label(self.root, image=self.bg_image)
        self.bg_label.grid(row = 0, column = 0, sticky = 'ne',)
        self.bg_label.place(relx=0, rely=0)
        
        if not hasattr(self, "img_record"):
            self.img_record = create_icon("recording.png")
        self.button_talk = tk.Button(self.root, text = 'Talk!', image=self.img_record.image, borderwidth=0, pady=0, padx=0, background="#13273a", 
                             command=lambda:self.stop_active_mode())
        self.button_talk.place(relx=0.935, rely=0.601)
        self.start_talk()
        
    def stop_active_mode(self):
        self.my_cortana.flag = False
        self.button_talk = tk.Button(self.root, text = 'Talk!', image=self.img_talk.image, borderwidth=0, pady=0, padx=0, background="#13273a", 
                             command=lambda:self.active_mode())
        self.button_talk.place(relx=0.935, rely=0.601)
        # Set background image
        bg_image = Image.open("./images/cover1.jpg")
        resized_img=bg_image.resize(self.monitor_size(0.5, 0.55), Image.LANCZOS)
        self.bg_image=ImageTk.PhotoImage(resized_img)
        self.bg_label = ttk.Label(self.root, image=self.bg_image)
        self.bg_label.grid(row = 0, column = 0, sticky = 'ne',)
        self.bg_label.place(relx=0, rely=0)
        self.buttons_regular()
        
    def regular_app_button(self):
        if self.lang_label is not None:
            self.lang_label.place_forget()
            self.param_label.place_forget()
        else:
            self.lang_label = None
            self.param_label = None
            
        if not hasattr(self, "img_talk"):
            self.img_talk = create_icon("icon1.png")
        
        if not hasattr(self, "img_open"):
            self.img_open = create_icon("icon-open.png")
        
        if not hasattr(self, "img_folder"):
            self.img_folder = create_icon("folder.png")

        if not hasattr(self, "img_plus"):
            self.img_plus = create_icon("plus.png")
    
        if not hasattr(self, "img_load"):
            self.img_load = create_icon("load.png")
            
        if not hasattr(self, "img_preprompt"):
            self.img_preprompt = create_icon("preprompt.png")
            
        self.button_enter = ttk.Button(self.root, text="Enter", width=100, 
                             command=lambda:self.start_chat(self.entry_prompt.get("1.0" , END)), )
        self.button_talk = tk.Button(self.root, text = 'Talk!', image=self.img_talk.image, borderwidth=0, pady=0, padx=0, background="#13273a", 
                             command=lambda:self.active_mode())
        self.button_file = ttk.Button(self.root, text = 'Open file', image=self.img_open.image, #borderwidth=0, pady=0, padx=0, background="white",
                             command=lambda:sp.Popen([programName, f'./results/{self.filename}.md']))
        self.button_folder = tk.Button(self.root, text = 'Folder', image=self.img_folder.image, borderwidth=0, pady=0, padx=0, background="#13273a",
                             command=lambda:os.startfile(self.folder_res))
        self.button_new = tk.Button(self.root, text = 'New', image=self.img_plus.image, borderwidth=0, pady=0, padx=0, background="#13273a",
                            command=lambda:self.new_filename())
        self.button_load = ttk.Button(self.root, text = 'Load', image=self.img_load.image, #borderwidth=0, pady=0, padx=0, background="#13273a",
                            command=lambda:self.load_from_file())
        self.button_preprompt = ttk.Button(self.root, text = 'PePrompt', image=self.img_preprompt.image, #borderwidth=0, pady=0, padx=0, background="#13273a",
                              command=lambda:sp.Popen([self.open_param, './model/preprompt.json']))
        self.button_enter.place(relx=0.5, rely=0.96, anchor="center")
        self.button_talk.place(relx=0.935, rely=0.601)
        self.button_file.place(relx=0.905, rely=0.025)
        self.button_folder.place(relx=0.88, rely=0.601)
        self.button_new.place(relx=0.77, rely=0.601)
        self.button_load.place(relx=0.905, rely=0.1)
        self.button_preprompt.place(relx=0.03, rely=0.51)
        self.create_button_api()
    
    def create_button_api(self):
        if not hasattr(self, "img_api"):
            self.img_api = create_icon("api.png")
        
        self.button_api = ttk.Button(self.root, text = 'api', image=self.img_api.image, #borderwidth=0, pady=0, padx=0, background="#13273a",
                              command=lambda:self.create_apikey())
        self.button_api.place(relx=0.03, rely=0.42)
        
    def create_apikey(self):
        self.button_api.place_forget()
        self.api_label = tk.Label(self.root, text="Enter API key from OpenAi")
        self.api_label.pack(pady=15, anchor=tk.CENTER)
        self.api_entry = tk.Entry(self.root)
        self.api_entry.pack(ipadx=60, pady=10, anchor=tk.CENTER)#ipadx=40, padx=35, pady=160, anchor='sw')
        self.button_ok = tk.Button(self.root, text="OK", command=self.remove_entry)
        self.button_ok.pack(pady=10, anchor=tk.CENTER)#padx=150, pady=160, anchor='w')
        
    def remove_entry(self):
        self.api_key = self.api_entry.get()
        encrypt_key(self.api_key, path='./api/')
        self.api_label.pack_forget()
        self.api_entry.pack_forget()
        self.button_ok.pack_forget()
        self.create_button_api()

    def launch_cortana(self, language, api_key):
        name = "gpt-4"
        api_key = None
        self.my_cortana = cortana(name, language, api_key=api_key)
        self.gif.unload()
        self.regular_app_button()
    
    def regular_cortana(self, language, api_key):
        name = "gpt-4"
        api_key = None
        self.my_cortana = cortana(name, language, api_key=api_key)
    
    def get_api_key(self):
        try:
            self.api_key = decrypt_key(path='./api/')
        except:
            self.create_apikey()
            self.api_key = decrypt_key(path='./api/')
        return self.api_key
    

root = tk.Tk()
app = CortanaApp(root)
root.mainloop()
