# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 22:28:00 2023

@author: ManuMan
"""

import tkinter as tk
root = tk.Frame()
t = tk.Text(root)
t.grid(row=0,column=0,columnspan=3)
root.grid()

def addLine():
  msg = lineField.get()
  t.insert("end",u"\n{}".format(msg))

def replaceLastLine():
  msg = lineField.get()
  t.delete("end-1l","end")
  t.insert("end",u"\n{}".format(msg))

lineField = tk.Entry(root)
lineField.grid(row=1,column=0)

addBtn = tk.Button(root,text="Add line",command=addLine)
addBtn.grid(row=1,column=1)

replBtn = tk.Button(root,text="Replace line",command=replaceLastLine)
replBtn.grid(row=1,column=2)

tk.mainloop()