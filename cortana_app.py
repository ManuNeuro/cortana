# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 08:48:47 2023

@author: ManuMan
"""
import os
from datetime import datetime
import customtkinter as ctk
from customtkinter import CTkTextbox, CTkImage, CTkFont, filedialog
from customtkinter import *
from tktooltip import ToolTip
from PIL import Image, ImageSequence
# from ctkthemes import ThemedStyle
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
    
markdown = kwargs['app']['markdown']
openParam = kwargs['app']['openParam']

# try:
#     from ctypes import windll  # Only exists on Windows.
#     myappid = "dorean.cortana.gpt4.0.1"
#     windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
# except ImportError:
#     pass

def create_icon(self, filename, icon_sizes = [(64,64)]):
    img = Image.open(f"./images/{filename}.png")
    img.save('icon.ico', sizes=icon_sizes)

def window_size_str():
    return str(int(GetSystemMetrics(0)/2.8)) + 'x' + str(GetSystemMetrics(1)/1.6)

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

def load_markdown_file(filename):
    with open(filename, 'r') as file:
        content = file.read()
    return content

class MarkdownOutput:
    def __init__(self, filename, captured_output=""):
        self.captured_output = captured_output
        self.filepath = f'./results/{filename}.md'
        self.programpath = markdown
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
    
def create_icon(self, filename):
    # Resizing image to fit on button
    icon=CTkImage(Image.open(f"./images/{filename}"), size=(30, 30))
    # Let us create a label for button event
    img_label= CTkLabel(self, image=icon, text='')
    img_label.image = icon # keep a reference!
    return img_label
    
class CortanaApp(ctk.CTk):
    def __init__(self):
        super().__init__()        
        self.title("CortanaGPT")
        # Get screen size
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        w = self.screen_width/2-100  #Width of the Window
        h = self.screen_height  #Height of the Window
        # get screen width and height
        ws = self.screen_width#This value is the width of the screen
        hs = self.screen_height#This is the height of the screen
        # calculate position x, y
        x = 0
        y = 0
        #This is responsible for setting the dimensions of the screen and where it is
        #placed
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        for col in range (0,11):
            self.grid_columnconfigure(col, pad=5, weight=1)
        for row in range (0,11):
            self.grid_rowconfigure(row, pad=5, weight=1)
        
        self.geometry(window_size_str())
        self.configure(fg_color="#13273a", bg_color = "#13273a")
        # self.set_default_color_theme("dark-blue")
        self.myfont = CTkFont(family="Helvetica", size=14)
        self.iconbitmap("icon.ico")
        self.autoreload_var = ctk.IntVar(value=0)
        self.checkbox_reload()
        
        # Initialization the app
        self.def_load()
        
        # Launching app buttons
        self.launching_app()
        
        # Create prompt
        self.create_prompt()
        
        # Rerouting all output to markdown file        
        self.markdown_output = MarkdownOutput(self.filename)
        sys.stdout = self.markdown_output     
        
    def create_prompt(self, row=9, column=0, sticky="ew", columnspan=11, 
                           padx=(10, 10), rowspan=1, pady=(0, 0)):
        # Interactive text box to chat with cortana
        self.entry_prompt = CTkTextbox(self, font=self.myfont)
        self.entry_prompt.insert("0.0", "Enter your question here...")
        self.entry_prompt.grid(row=row, column=column, sticky="ew", columnspan=columnspan, 
                               padx=padx, rowspan=rowspan, pady=pady)
        
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
        sp.Popen([markdown, f'./results/{self.filename}.md'])
        self.markdown_output = MarkdownOutput(self.filename, last_messages)
        sys.stdout = self.markdown_output

    def def_load(self):
        if not hasattr(self, "filename"):
            self.new_filename()
            self.open_param = openParam
            self.param_path = "./model/parameters.json"
            self.folder_res = path = os.path.realpath('./results/')
            
            # Set background image
            self.bg_image=CTkImage(Image.open("./images/cover.jpg"), size=self.monitor_size(0.37, 0.35))
            self.bg_label = ctk.CTkLabel(self, text='', image=self.bg_image)
            self.bg_label.place(relx=0, rely=0)
            
            self.create_widgets_gif('cortana_opening')

    def create_widgets_gif(self, filename):
        resize_gif(filename, self.monitor_size(0.25, 0.5))
        filepath = f"./images/{filename}_resized.gif"
        # label_gif = ctk.CTkLabel(self)
        self.gif = ImageLabel(self)
        self.gif.load(filepath, self.monitor_size(0.2, 0.35))       
        self.gif.place(relx=0.25, rely=0.0)
        self.launch_gif()
    
    def launch_gif(self):
        threading.Thread(target=self.gif.next_frame()).start()
          
    def talk_with_cortana(self, **kwargs):
        self.my_cortana.talk_with_cortana(**kwargs)
        
        # Vocal command to quit
        if not self.my_cortana.flag:
            self.stop_active_mode()
        
        
    def chat_with_cortana(self, *args, **kwargs):
        self.my_cortana.submit_prompt(*args, _voice=False, **kwargs)
        '''
        In theory the following code should kill the app and launch it again as
        soon as the answer is generated, but this won't work if there are
        multiple tabs open in marktext. 
        
        At the end of the day, I prefer to have to do the refresh manually than
        the app having to load over and over each time there is an answer.
        
        Add the following code if you want the "auto-reload":
        '''
        if self.autoreload:
            self.markdown_output.process.terminate()
            self.markdown_output.process = sp.Popen([self.markdown_output.programpath, 
                                                     self.markdown_output.filepath])  
        
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
        self.create_dropdown_model(True)
        self.create_dropdown_role(True)
        self.button_language()
        self.button_parameter()  
    
    def create_dropdown_model(self, landing_page=False):
        
        if landing_page:

            # Dropdown menu options
            options = [
                "gpt-4",
                "gpt-4-32k",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
            ]
              
            # Create Dropdown menu
            self.label_model = ctk.CTkLabel(self, text="Model", text_color='cyan', bg_color="#13273a", height=18)
            self.drop_model = ctk.CTkComboBox(self, state="readonly", values=options, bg_color='#13273a', command=self.change_model) 
            ToolTip(self.drop_model, msg="Select the LLM model you want to use. 16k and 32k indicate the number of token in memory.", delay=1.0)
    
            self.drop_model.set(options[0])
            self.change_model(options[0], True)
            self.label_model.grid(row = 8, column = 0, padx=(0, 100), pady=(70, 5))
            self.drop_model.grid(row = 8, column = 0, padx=(0, 0), pady=(130, 10))
        else:
            self.label_model.grid(row = 8, column = 0, padx=(0, 100), pady=(10, 10))
            self.drop_model.grid(row = 8, column = 0, padx=(0, 0), pady=(60, 10))
    
    def create_dropdown_role(self, landing_page=False):
        # Dropdown menu options
        if landing_page:

            with open('./model/preprompt.json') as json_file:
                kwargs = json.load(json_file)
            roles = kwargs['roles']
            options = [role for role in roles.keys()]
            
            # Create Dropdown menu
            self.label_role = ctk.CTkLabel(self, text="Role", text_color='cyan', bg_color="#13273a", height=18)
            self.drop_role = ctk.CTkComboBox(self, state="readonly", values=options, bg_color='#13273a', command=self.change_role) 
            ToolTip(self.drop_role, msg="Select the role you want the AI to play. Check the preprompt button to know what the roles are.\n"\
                                        "You can add any role you want in the json, it will automatically add the role name in the list", delay=1.0)
    
            self.drop_role.set(options[0])
            self.change_role(options[0])
            self.label_role.grid(row = 8, column = 1, padx=(0, 100), pady=(70, 5))
            self.drop_role.grid(row = 8, column = 1, padx=(0, 0), pady=(130, 10))
        else:
            self.label_role.grid(row = 8, column = 1, padx=(0, 100), pady=(10, 10))
            self.drop_role.grid(row = 8, column = 1, padx=(0, 0), pady=(60, 10))
            
    def change_role(self, role, event=True):
        self.role = role
        if event:
            # ctk.messagebox.showinfo(
            #     title="Model Selection",
            #     message=f"Selected role: {self.role}"
            # )
            if hasattr(self, "my_cortana"):
                self.my_cortana.set_role(self.role)

    def change_model(self, model, event=True):
        self.model_name = model
        if event:
            # ctk.messagebox.showinfo(
            #     title="Model Selection",
            #     message=f"Selected model: {self.model_name}"
            # )
            if hasattr(self, "my_cortana"):
                self.my_cortana.set_model(self.model_name)

    def button_language(self):
        self.lang_label = ctk.CTkLabel(self, text="Select language!", text_color='white', bg_color="#19344d")
        self.button_fr = ctk.CTkButton(self, text="En", bg_color="#19344d", width=70,
                                       command=lambda:self.launch_cortana('english', api_key=self.get_api_key(), role=self.role))
        self.button_en = ctk.CTkButton(self, text="Fr", bg_color="#19344d", width=70, 
                                       command=lambda:self.launch_cortana('french', api_key=self.get_api_key(), role=self.role))
        self.button_fr.grid(row = 0, column = 0, padx=(5, 10), pady=(10, 0))
        self.button_en.grid(row = 0, column = 0, padx=(5, 10), pady=(80, 0))
        self.lang_label.grid(row = 0, column = 0, padx=(5, 10), pady=(150, 0))

    def button_parameter(self):
        self.param_label = ctk.CTkLabel(self, text="Provide path to markdown editor!", text_color='white')
        self.param_label.grid(row = 8, column = 4, padx=(0, 0), pady=(130, 10))
        if not hasattr(self, "img_param"):
            self.img_param = create_icon(self, "param.png")
        self.button_param = ctk.CTkButton(self, image=self.img_param.image, width=10, height=10,
                                          border_width=0, fg_color="#13273a", bg_color="#13273a",# background="#13273a",
                                      command=lambda:sp.Popen([self.open_param, self.param_path]))
        self.button_param.grid(row = 8, column = 5, padx=(0, 0), pady=(130, 10))
        ToolTip(self.button_param, msg="Open the parameter json file. The first you launch the app you must provide the markdown editor path.", delay=1.0)

    
    def buttons_regular(self):
        self.button_fr = ctk.CTkButton(self, text="En", bg_color="#13273a", width=70,
                                       command=lambda:self.launch_cortana('english', api_key=self.get_api_key(), role=self.role))
        self.button_en = ctk.CTkButton(self, text="Fr", bg_color="#13273a", width=70, 
                                       command=lambda:self.launch_cortana('french', api_key=self.get_api_key(), role=self.role))
        self.button_fr.grid(row = 0, column = 0, padx=(5, 10), pady=(10, 0))
        self.button_en.grid(row = 0, column = 0, padx=(5, 10), pady=(80, 0))
        self.regular_app_button()
        
        # self.create_prompt(row=11, column=0, padx=(10, 10))
        
    def active_mode(self):
        # Set background image
        self.bg_image=CTkImage(Image.open("./images/cover-rec.png"), size=self.monitor_size(0.37, 0.35))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text='')
        self.bg_label.place(relx=0, rely=0)
        self.button_enter.grid_remove()
        self.drop_model.grid_remove()
        self.label_model.grid_remove()
        self.button_talk.grid_remove()
        self.button_preprompt.grid_remove()
        self.check_autoreload.grid_remove()

        if not hasattr(self, "img_record"):
            self.img_record = create_icon(self, "recording.png")
        self.button_talk = ctk.CTkButton(self, image=self.img_record.image, border_width=0 , 
                                     bg_color="#13273a", fg_color="#13273a",
                                     width=20, height=20,
                                     command=lambda:self.stop_active_mode())
        self.button_talk.grid(row = 8, column = 9, padx=(0, 0), pady=(60, 10))
        ToolTip(self.button_talk, msg="Close the active conversation mode.", delay=1.0)

        self.start_talk()
    
    def stop_active_mode(self):
        self.my_cortana.flag = False
        self.button_param.grid_remove()
        self.button_talk = ctk.CTkButton(self, image=self.img_talk.image, border_width=0 , 
                                     bg_color="#13273a", fg_color="#13273a",
                                     width=20, height=20,
                                     command=lambda:self.stop_active_mode())
        self.button_talk.grid(row = 8, column = 9, padx=(0, 0), pady=(60, 10))
        # Set background image
        self.bg_image = CTkImage(Image.open("./images/cover.jpg"), size=self.monitor_size(0.37, 0.35))
        self.bg_label = ctk.CTkLabel(self, text='', image=self.bg_image)
        self.bg_label.place(relx=0, rely=0)
        self.buttons_regular()
        self.create_prompt()
    
    def regular_app_button(self):
        
        self.button_param.grid_remove()
        self.drop_model.grid_remove()
        self.drop_role.grid_remove()
        self.label_model.grid_remove()
        self.label_role.grid_remove()
        self.create_dropdown_model()
        self.create_dropdown_role()
        
        if self.lang_label is not None:
            self.lang_label.grid_remove()
            self.param_label.grid_remove()
        else:
            self.lang_label = None
            self.param_label = None
            
        if not hasattr(self, "img_talk"):
            self.img_talk = create_icon(self, "icon1.png")
        
        if not hasattr(self, "img_open"):
            self.img_open = create_icon(self, "icon-open.png")
        
        if not hasattr(self, "img_folder"):
            self.img_folder = create_icon(self, "folder.png")

        if not hasattr(self, "img_plus"):
            self.img_plus = create_icon(self, "plus.png")
    
        if not hasattr(self, "img_load"):
            self.img_load = create_icon(self, "load.png")
            
        if not hasattr(self, "img_preprompt"):
            self.img_preprompt = create_icon(self, "preprompt.png")
            
        self.button_enter = ctk.CTkButton(self, text="Enter", 
                                          command=lambda:self.start_chat(self.entry_prompt.get("1.0" , END)), )
        self.button_talk = ctk.CTkButton(self, image=self.img_talk.image, border_width=0, 
                                         bg_color="#13273a", fg_color="#13273a",
                                         width=20, height=20,
                                         command=lambda:self.active_mode())
        ToolTip(self.button_talk, msg="Launch the active conversation mode, have fun!", delay=1.0)
        
        self.button_file = ctk.CTkButton(self, image=self.img_open.image, border_width=0 , 
                                         bg_color="#13273a",
                                         width=50, height=20, #borderwidth=0, pady=0, padx=0, background="white",
                                         command=lambda:sp.Popen([markdown, f'./results/{self.filename}.md']))
        ToolTip(self.button_file, msg="Open the current markdown file in conversation", delay=1.0)
        
        self.button_folder = ctk.CTkButton(self, image=self.img_folder.image, border_width=0, 
                                        bg_color="#13273a", fg_color="#13273a",
                                        width=50, height=20,
                                        command=lambda:os.startfile(self.folder_res))
        ToolTip(self.button_folder, msg="Open the folder where markdown files are stored", delay=1.0)
        
        self.button_new = ctk.CTkButton(self, image=self.img_plus.image, border_width=0, 
                                        bg_color="#13273a", fg_color="#13273a",
                                        width=20, height=20,
                                        command=lambda:self.new_filename())
        ToolTip(self.button_new, msg="Open conversation in a new file", delay=1.0)
        
        self.button_load = ctk.CTkButton(self, image=self.img_load.image, bg_color="#13273a",
                                         width=50, height=20,#borderwidth=0, pady=0, padx=0, background="#13273a",
                                         command=lambda:self.load_from_file())
        ToolTip(self.button_load, msg="Load an existing markdown file", delay=1.0)

        self.button_preprompt = ctk.CTkButton(self, image=self.img_preprompt.image, bg_color="#13273a",
                                              width=50, height=20,#borderwidth=0, pady=0, padx=0, background="#13273a",
                                              command=lambda:sp.Popen([self.open_param, './model/preprompt.json']))
        ToolTip(self.button_preprompt, msg="Open the preprompt parameter to customize your Cortana", delay=1.0)

        self.check_autoreload = ctk.CTkCheckBox(self, variable=self.autoreload_var, command=self.checkbox_reload,
                                                text='Auto reload', onvalue=1, offvalue=0, bg_color="#13273a", text_color='cyan')
        ToolTip(self.check_autoreload, msg="Automatically close and reopen the markdown file", delay=1.0)   # True by default
        
        self.button_param = ctk.CTkButton(self, image=self.img_param.image, width=10, height=10,
                                          border_width=0, fg_color="#13273a", bg_color="#13273a",# background="#13273a",
                                      command=lambda:sp.Popen([self.open_param, self.param_path]))
        ToolTip(self.button_param, msg="Parameters of the app, open the json file", delay=1.0)   # True by default

        self.button_talk.grid(row = 8, column = 9, padx=(0, 0), pady=(60, 10))
        self.button_folder.grid(row = 8, column = 8, padx=(0, 0), pady=(60, 10))
        self.button_new.grid(row = 8, column = 7, padx=(0, 0), pady=(60, 10))
        self.button_param.grid(row = 8, column = 5, padx=(0, 0), pady=(60, 10))
        
        self.button_file.grid(row = 7, column = 10, padx=(50, 0), pady=(100, 10))
        self.button_load.grid(row = 7, column = 10, padx=(50, 0), pady=(180, 0))
        self.check_autoreload.grid(row = 8, column = 10, padx=(10, 10), pady=(5, 0))
        
        self.button_preprompt.grid(row = 7, column = 0, padx=(0, 10), pady=(200, 0))
        self.create_button_api()
    
        self.button_enter.grid(row = 10, column = 0, columnspan=11, sticky='sew', padx=(10, 10), pady=(0, 10))
   
    def checkbox_reload(self):
        self.autoreload = self.autoreload_var.get()
    
    def create_button_api(self):
        if not hasattr(self, "img_api"):
            self.img_api = create_icon(self, "api.png")
        
        self.button_api = ctk.CTkButton(self, image=self.img_api.image, 
                                        bg_color="#13273a",
                                        width=50, height=20,#borderwidth=0, pady=0, padx=0, background="#13273a",
                                        command=lambda:self.create_apikey())
        self.button_api.grid(row = 7, column = 0, padx=(100, 0), pady=(200, 0))
        
    def create_apikey(self):
        self.button_api.place_forget()
        self.api_label = ctk.CTkLabel(self, text="Enter API key from OpenAi")
        self.api_label.pack(pady=15, anchor=ctk.CENTER)
        self.api_entry = ctk.Entry(self)
        self.api_entry.pack(ipadx=60, pady=10, anchor=ctk.CENTER)#ipadx=40, padx=35, pady=160, anchor='sw')
        self.button_ok = ctk.CTkButton(self, text="OK", command=self.remove_entry)
        self.button_ok.pack(pady=10, anchor=ctk.CENTER)#padx=150, pady=160, anchor='w')
        
    def remove_entry(self):
        self.api_key = self.api_entry.get()
        encrypt_key(self.api_key, path='./api/')
        self.api_label.pack_forget()
        self.api_entry.pack_forget()
        self.button_ok.pack_forget()
        self.create_button_api()

    def launch_cortana(self, language, api_key, role):
        api_key = None
        self.my_cortana = cortana(self.model_name, language, api_key=api_key, role=role)
        self.gif.unload()
        self.regular_app_button()
    
    def regular_cortana(self, language, api_key):
        api_key = None
        self.my_cortana = cortana(self.model_name, language, api_key=api_key)
    
    def get_api_key(self):
        try:
            self.api_key = decrypt_key(path='./api/')
        except:
            self.create_apikey()
            self.api_key = decrypt_key(path='./api/')
        return self.api_key
    

app = CortanaApp()
app.mainloop()
