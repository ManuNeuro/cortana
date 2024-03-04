# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 08:48:47 2023

@author: ManuMan
"""
import os
import sys
import threading
import json
import numpy as np
import subprocess as sp
from win32api import GetSystemMetrics
import gc
import weakref
import signal 
from datetime import datetime
import numpy as np

import customtkinter as ctk
from customtkinter import CTkTextbox, CTkImage, CTkFont, filedialog
from PIL import Image, ImageSequence

from cortana.api.encrypt import decrypt_key
from cortana.model.external_classes import ToplevelWindow, ImageLabel, MarkdownOutput
from cortana.model.cortana_class import Cortana
from cortana.model.utils import resize_gif
from cortana.model.buttons import (create_dropdown_model, create_dropdown_role, launch_language, 
                                   launch_parameter, regular_app_layout, active_mode, stop_active_mode,
                                   checkbox_function, create_apikey)

basedir = os.path.dirname(__file__)

with open(os.path.join(basedir, 'model', 'parameters.json')) as json_file:
    kwargs = json.load(json_file)
    
markdown = kwargs['app']['markdown']
openParam = kwargs['app']['openParam']

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = "dorean.cortana.gpt.0.3"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class CortanaApp(ctk.CTk):
    def __init__(self):
        super().__init__()        
        self.title("CortanaGPT")
        
        # Get screen size
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        w = self.screen_width/2  #Width of the Window
        h = self.screen_height - 30 #Height of the Window
        # Position of window
        x, y = 0, 0
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        # Definition of the grid
        for col in range (0,11):
            self.grid_columnconfigure(col, pad=5, weight=1)
        for row in range (0,11):
            self.grid_rowconfigure(row, pad=5, weight=1)
        
        # Configure the app                    
        self.configure(fg_color="#13273a", bg_color = "#13273a")
        self.myfont = CTkFont(family="Helvetica", size=14)
        self.iconbitmap(os.path.join(basedir, "icon.ico"))
        
        # Initialization of variables
        self.autoreload_var = ctk.IntVar(value=0)
        checkbox_function(self)
        self.role = None
        
        # Initialization the app
        self.def_load()
        
        # Launching app buttons
        self.launching_app()
        
        # Create prompt
        self.create_prompt()
        
        # Rerouting all output to markdown file        
        self.markdown_output = MarkdownOutput(self.filename)
        sys.stdout = self.markdown_output     
  
    @staticmethod
    def monitor_size(x_ratio, y_ratio):
        return int(GetSystemMetrics(0)*x_ratio), int(GetSystemMetrics(1)*y_ratio)  
  
    def launch_gif(self):
        threading.Thread(target=self.gif.next_frame()).start()  
  
    def launching_app(self):
        create_dropdown_model(self, True)
        create_dropdown_role(self, True)
        launch_language(self)
        launch_parameter(self)  
    
    def launch_cortana(self, language, api_key, role, **kwargs):
        self.my_cortana = Cortana(self.model_name, language, api_key=api_key, role=role, **kwargs['text'])
        if self.gif is not None:
            self.gif.unload()
            self.gif = None
        regular_app_layout(self)  
        
    def create_prompt(self, row=9, column=0, sticky="ew", columnspan=11, 
                           padx=(10, 10), rowspan=1, pady=(0, 0)):
        # Interactive text box to chat with cortana
        self.entry_prompt = CTkTextbox(self, font=self.myfont)
        self.entry_prompt.insert("0.0", "Enter your question here...")
        self.entry_prompt.grid(row=row, column=column, sticky="ew", columnspan=columnspan, 
                               padx=padx, rowspan=rowspan, pady=pady)
        
    def new_filename(self):       
        date = datetime.now()
        date_str = date.strftime('%Y-%m-%d')
        rnd_tag = np.random.randint(1, 1000000)
        filename = f'{date_str}_historic#{rnd_tag}' 
        if hasattr(self, 'filename'): # If this is not the first time
            self.markdown_output = MarkdownOutput(filename)
            sys.stdout = self.markdown_output
            self.my_cortana.reset_messages()
        self.filename = filename
    
    def def_load(self):
        if not hasattr(self, "filename"):
            self.new_filename()
            self.toplevel_window = None
            self.open_param = openParam
            self.param_path = os.path.join(basedir, 'model', 'parameters.json')
            self.prepromt_path = os.path.join(basedir, 'model', 'preprompt.json')
            self.folder_res = os.path.join(basedir, 'results')
            self.folder_images = os.path.join(basedir, 'images')
            self.folder_api = os.path.join(basedir, 'api')
            
            # Set background image
            filepath = os.path.join(self.folder_images, "cover.jpg")
            self.bg_image = CTkImage(Image.open(filepath), size=self.monitor_size(0.37, 0.35))
            self.bg_label = ctk.CTkLabel(self, text='', image=self.bg_image)
            self.bg_label.place(relx=0, rely=0)
            
            self.create_widgets_gif('cortana_opening')

    def create_widgets_gif(self, filename):
        resize_gif(filename, self.monitor_size(0.25, 0.5))
        filepath = os.path.join(self.folder_images, f"{filename}_resized.gif")
        # label_gif = ctk.CTkLabel(self)
        self.gif = ImageLabel(self)
        self.gif.load(filepath, self.monitor_size(0.2, 0.35))       
        self.gif.place(relx=0.25, rely=0.0)
        self.launch_gif()
    
    def talk_with_cortana(self, **kwargs):
        # Opening active mode display
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self)  # create window if its None or destroyed
        else:
            self.toplevel_window.focus()  # if window exists focus it

        self.my_cortana.talk_with_cortana(preprompt_path=self.prepromt_path, **kwargs)
        
        
        # Vocal command to quit
        if not self.my_cortana.flag:
            stop_active_mode(self)
        
        
    def chat_with_cortana(self, *args, **kwargs):
        self.my_cortana.submit_prompt(*args, _voice=False, preprompt_path=self.prepromt_path, **kwargs)

        if self.autoreload:
            self.markdown_output.process.terminate()
            self.markdown_output.process = sp.Popen([self.markdown_output.programpath, 
                                                     self.markdown_output.filepath])  
        
    def start_talk(self):
        with open(self.param_path) as json_file:
            kwargs = json.load(json_file)
            
        # Create a separate thread to run the on_button_click function
        self.my_cortana.flag = True
        threading.Thread(target=self.talk_with_cortana, kwargs=kwargs).start()
        
    def start_chat(self, input_text):
        with open(self.param_path) as json_file:
            kwargs = json.load(json_file)
            
        # Create a separate thread to run the on_button_click function
        threading.Thread(target=self.chat_with_cortana, args=[input_text], kwargs=kwargs).start()
        self.entry_prompt.delete("1.0" , ctk.END)
    
    def change_role(self, role, event=True):
        self.role = role
        if hasattr(self, "my_cortana"):
            if event:
                # ctk.messagebox.showinfo(
                #     title="Model Selection",
                #     message=f"Selected role: {self.role}"
                # )
                self.my_cortana.set_role(self.role, print_=True)
            else:
                self.my_cortana.set_role(self.role, print_=False)


    def change_model(self, model, event=True):
        self.model_name = model
        
        # ToDo: add parameter memory type: 'all' or 'summary'
        
        if hasattr(self, "my_cortana"):
            if event:
                # ctk.messagebox.showinfo(
                #     title="Model Selection",
                #     message=f"Selected model: {self.model_name}"
                # )            
                self.my_cortana.set_model(self.model_name, print_=True, **kwargs['text'])
            else:
                self.my_cortana.set_model(self.model_name, print_=False, **kwargs['text'])

    
    def remove_from_grid(self, names):
        attribute_names = np.array([attr for attr in self.__dict__.keys()])
        if isinstance(names, str):
            names = []
        
        for name in names:
            idx_to_remove = [name in attr for attr in attribute_names]
            attributes_to_remove = attribute_names[idx_to_remove]
            
            for attribute in attributes_to_remove:
                self.__dict__[attribute].grid_remove()
    
    def get_api_key(self):
        try:
            self.api_key = decrypt_key(path=self.folder_api)
        except:
            create_apikey(self)
            self.api_key = decrypt_key(path=self.folder_api)
        return self.api_key
    

app = CortanaApp()
app.mainloop()
