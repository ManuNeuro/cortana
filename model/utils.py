# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 09:44:14 2023

@author: ManuMan
"""
import os
import os
import sys
import json
import subprocess as sp
from itertools import count
from win32api import GetSystemMetrics

from PIL import Image, ImageSequence
from customtkinter import CTkTextbox, CTkImage, CTkFont, filedialog, CTkLabel, CTkTextbox
import customtkinter as ctk

basedir = os.path.dirname(__file__).split('model')[0]

def window_size_str():
    return str(int(GetSystemMetrics(0)/2.8)) + 'x' + str(GetSystemMetrics(1)/1.6)

def generate_icon(filename, icon_sizes = [(64,64)]):
    filepath = os.path.join(basedir, 'images', f"{filename}.png")
    img = Image.open(filepath)
    img.save('icon-active.ico', sizes=icon_sizes)


def resize_gif(filename, size):
    
    # Open source
    filepath = os.path.join(basedir, 'images', f"{filename}.gif")
    im = Image.open(filepath)
    
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
    filepath = os.path.join(basedir, 'images', f"{filename}_resized.gif")
    om.save(filepath,  save_all=True, append_images=list(frames))
    
def load_markdown_file(filepath):
    with open(filepath, 'r') as file:
        content = file.read()
    return content

    
def create_icon(self, filename):
    # Resizing image to fit on button
    filepath = os.path.join(basedir, 'images', filename)
    icon=CTkImage(Image.open(filepath), size=(30, 30))
    # Let us create a label for button event
    img_label= CTkLabel(self, image=icon, text='')
    img_label.image = icon # keep a reference!
    return img_label
    