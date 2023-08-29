# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 12:20:20 2023

@author: ManuMan
"""
import os
import tkinter as tk
from tkinter import ttk
from tkinter import Text, font, filedialog
from tkinter import *
from PIL import Image,ImageTk, ImageSequence
import subprocess as sp


# photo=Image.open("./images/icon1.png")
# # Resizing image to fit on button
# resized_img=photo.resize((30,30),Image.LANCZOS)
# icon=ImageTk.PhotoImage(resized_img)
# # Let us create a label for button event
# img_label= Label(image=icon)
# img_label.image = icon # keep a reference!


def create_icon(filename):
    photo=Image.open(f"./images/{filename}")
    # Resizing image to fit on button
    resized_img=photo.resize((30,30),Image.LANCZOS)
    icon=ImageTk.PhotoImage(resized_img)
    # Let us create a label for button event
    img_label= Label(image=icon)
    img_label.image = icon # keep a reference!
    return img_label
    
class ButtonApp():
    
    def __init__(self, root):
        super(ButtonApp, self).__init__()
        self.root = root
        # Launching app buttons

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