# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 19:25:35 2023

@author: ManuMan
"""

from tkinter import *
from tkinter import font , filedialog
from markdown2 import Markdown
from tkhtmlview import HTMLLabel
from tkinter import messagebox as mbox

# https://www.freecodecamp.org/news/lets-create-a-toy-markdown-editor-with-python-tkinter/

class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.myfont = font.Font(family="Helvetica", size=14)
        self.init_window()
        
        self.inputeditor = Text(self, width="1")
        self.inputeditor.pack(fill=BOTH, expand=1, side=LEFT)
    
        self.outputbox = HTMLLabel(self, width="1", background="black", html='<h1 style="color: cyan; text-align: center"> Cortana </H1>')
        self.outputbox.pack(fill=BOTH, expand=1, side=RIGHT)
        self.outputbox.fit_height()
        
        self.mainmenu = Menu(self)
        self.filemenu = Menu(self.mainmenu)
        self.filemenu.add_command(label="Open", command=self.openfile)
        self.filemenu.add_command(label="Save as", command=self.savefile)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.quit)
        self.mainmenu.add_cascade(label="File", menu=self.filemenu)
        self.master.config(menu=self.mainmenu)
        
        self.inputeditor.bind("<<Modified>>", self.onInputChange)
        
    def init_window(self):
        self.master.title("TDOWN")
        self.pack(fill=BOTH, expand=1)
        
    def onInputChange(self , event):
        self.inputeditor.edit_modified(0)
        md2html = Markdown()
        self.outputbox.set_html('<div style="color: cyan">'+md2html.convert(self.inputeditor.get("1.0" , END))+'</div>')
    
    def openfile(self):
        openfilename = filedialog.askopenfilename(filetypes=(("Markdown File", "*.md , *.mdown , *.markdown"),
                                                                      ("Text File", "*.txt"), 
                                                                      ("All Files", "*.*")))
        if openfilename:
            try:
                self.inputeditor.delete(1.0, END)
                self.inputeditor.insert(END , open(openfilename).read())
            except:
                print("Cannot Open File!") 
    
    def savefile(self):
        filedata = self.inputeditor.get("1.0" , END)
        savefilename = filedialog.asksaveasfilename(filetypes = (("Markdown File", "*.md"),
                                                                  ("Text File", "*.txt")) , title="Save Markdown File")
        if savefilename:
            try:
                f = open(savefilename , "w")
                f.write(filedata)
            except:
                mbox.showerror("Error Saving File" , "Oops!, The File : {} can not be saved!".format(savefilename))

    
root = Tk()
root.geometry("700x600")
app = Window(root)
app.mainloop()