import tkinter as tk

class ToggleButton(tk.Button):
	
	def __init__(self,parent,text,state):
		self.parent = parent
		self.text = text
		self.state = state
		btn = tk.Button(parent,text=text,command=toggle(state))
		btn.pack()
		if state == 'on':
			btn.config(relief='sunken')
		else:
			btn.config(relief='raised')
	
	def toggle(self,state):
		self.state = state
		if state == 'on':
			self.config(relief='sunken')
		else:
			self.config(relief='raised')

root = tk.Tk()

btn1 = ToggleButton(root,'GAIN','on')