# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 09:12:01 2023

@author: ManuMan
"""
import os
import sys
import json
import subprocess as sp
from itertools import count

from PIL import Image, ImageSequence
from customtkinter import CTkTextbox, CTkImage, CTkFont, filedialog, CTkLabel, CTkTextbox
import customtkinter as ctk


basedir_model = os.path.dirname(__file__)

class ImageLabel(ctk.CTkLabel):
    
    def load(self, im, size):
        if isinstance(im, str):
            im = Image.open(im)
        self.loc = 0
        self.frames = []

        try:
            for i in count(1):
                self.frames.append(CTkImage(im.copy(), size=size))
                im.seek(i)
        except EOFError:
            pass

        try:
            self.delay = int(im.info['duration'] * 1.6)
        except:
            self.delay = 100

        if len(self.frames) == 1:
            self.configure(image=self.frames[0])
        else:
            self.next_frame()

    def unload(self):
        self.configure(image="")
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.loc += 1
            self.loc %= len(self.frames)
            self.configure(image=self.frames[self.loc])
            self.after(self.delay, self.next_frame)


class MarkdownOutput:
    def __init__(self, filename, captured_output=""):
        with open(os.path.join(basedir_model, 'parameters.json')) as json_file:
            kwargs = json.load(json_file)
        self.captured_output = captured_output
        self.filepath = os.path.join(basedir_model.split('model')[0], 'results', f"{filename}.md")
        self.programpath = kwargs['app']['markdown']
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

###############################################################################
# Second window
###############################################################################

class RedirectedPrint:
    def __init__(self, output_text):
        self.output_text = output_text
        self.counter = 0

    def write(self, text):
            self.counter += 1
            self.output_text.configure(state="normal")  # configure textbox to be read-only
            self.output_text.insert(ctk.END, text)
            self.output_text.see(ctk.END)
            self.output_text.configure(state="disabled")
            
    def flush(self):
        pass


class ToplevelWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.title("Active mode console")
        # Get screen size
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.iconbitmap(os.path.join(basedir_model.split('model')[0], "icon-active.ico"))
        w = self.screen_width/3#Width of the Window
        h = self.screen_height  #Height of the Window
        # calculate position x, y
        x = w*1.5
        y = 0
        #This is responsible for setting the dimensions of the screen and where it is
        #placed
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        for col in range (0,11):
            self.grid_columnconfigure(col, pad=5, weight=1)
        for row in range (0,11):
            self.grid_rowconfigure(row, pad=5, weight=1)
        self.configure(fg_color='#13273a', bg_color = '#13273a')
        self.output_text = CTkTextbox(self, wrap=ctk.WORD, bg_color="#13273a", 
                                      fg_color="black", text_color="cyan")
        self.output_text.grid(row=0, column=0, rowspan=10, columnspan=11, sticky='nsew',
                              padx=(10, 10), pady=(10, 10))
        sys.stdout = RedirectedPrint(self.output_text)
        
        self.img_record = self.create_icon("recording.png")
        self.label = ctk.CTkLabel(self, text="Active mode", text_color='cyan',
                                  bg_color="#13273a", height=18)
        self.label.grid(row=10, column=0, pady=(10, 10))
        self.icon = ctk.CTkLabel(self, image=self.img_record.image,
                                  bg_color="#13273a", height=18)
        self.icon.grid(row=10, column=0, pady=(0, 10), padx=(10, 120))
        
    def create_icon(self, filename):
        # Resizing image to fit on button
        filepath = os.path.join(basedir_model.split('model')[0], 'images', filename)
        icon=CTkImage(Image.open(filepath), size=(30, 30))
        # Let us create a label for button event
        img_label= CTkLabel(self, image=icon, text='')
        img_label.image = icon # keep a reference!
        return img_label
    
    def output_state(self, active=True):
        if active:
            self.output_text.configure(state="normal")  # configure textbox to be read-only
        else:
            self.output_text.configure(state="disabled")  # configure textbox to be read-only

# app = ToplevelWindow()
# app.mainloop()