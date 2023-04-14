# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 14:13:02 2023

@author: ManuMan
"""

import tkinter as tk
from tkinter import Text
from PIL import ImageTk
from cortana import button_click
import sys
import threading

class RedirectedPrint:
    def __init__(self, output_text):
        self.output_text = output_text
        self.counter = 0

    def write(self, text):
            self.counter += 1
            # current_text = self.output_label.get("text")  # Get the current text
            # updated_text = current_text + text  # Concatenate the new text with the current text
            # self.output_label.config(text=updated_text)  # Update the label with the updated text
            self.output_text.insert(tk.END, text)
            self.output_text.see(tk.END)

    def flush(self):
        pass


class RedirectedPrint:
    def __init__(self, output_text):
        self.output_text = output_text

    def write(self, text):
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)

    def flush(self):
        pass

class MyApp:
    def __init__(self, root):
        # Set the window size
        self.root = root
        self.root.geometry("600x650")
        self.root.title("Cortana + chatGPT3.5")
        
        # Set background image
        self.bg_image = ImageTk.PhotoImage(file="cortana.png")
        bg_label = tk.Label(self.root, image=self.bg_image)
        bg_label.place(x=0, y=-70, relwidth=1, relheight=1)

        # Create a label for the entry widget
        entry_label_left = tk.Label(self.root, text="Enter your API key from openai:")
        entry_label_left.place(relx=0.1, rely=0.5)
        
        # Set entry
        self.entry = tk.Entry(root)
        self.entry.place(relx=0.4, rely=0.5)

        # Create a label for the entry widget (below)
        entry_label_below = tk.Label(root, text="API key is not stored and only use within a session")
        entry_label_below.place(relx=0.3, rely=0.6)
       
        # Create three buttons
        button1 = tk.Button(root, text="English", command=lambda:self.on_button_click_thread('english', api_key=self.entry.get()))
        button2 = tk.Button(root, text="French", command=lambda:self.on_button_click_thread('french', api_key=self.entry.get()))
        
        button1.place(relx=0.45, rely=0.7)
        button2.place(relx=0.55, rely=0.7)

        self.output_text = Text(root, wrap=tk.WORD, bg="black", fg="cyan")
        self.output_text.place(relx=0.5, rely=0.9, anchor="center", width=600, height=150)

        sys.stdout = RedirectedPrint(self.output_text)

    def on_button_click_thread(self, *arg, **kwargs):
        # Create a separate thread to run the on_button_click function
        threading.Thread(target=button_click, args=arg, kwargs=kwargs).start()


root = tk.Tk()
app = MyApp(root)
root.mainloop()
