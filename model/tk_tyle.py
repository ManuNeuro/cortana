# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 11:15:10 2023

@author: ManuMan
"""

import tkinter as tk
from tkinter import ttk

# Create a new style
style = ttk.Style()

# Configure the style for the button
style.configure("TButton",
                foreground="black",
                background="white",
                font=("Arial", 15, "bold"),
                padding=10)

# Configure the style for the label
style.configure("TLabel",
                foreground="black",
                background="white",
                font=("Arial", 15),
                padding=10)