import tkinter as tk
from tkinter import font as tkfont
import random
import sys
import NormalGrid as normal
import HexGrid as hex
sys.setrecursionlimit(15000)

class App(tk.Tk):
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

		container = tk.Frame(self)
		container.pack(side="top", fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)

		self.frames = {}
		for F in (MenuScreen, Game):
			page_name = F.__name__
			frame = F(parent=container, controller=self)
			self.frames[page_name] = frame
			frame.grid(row=0, column=0, sticky="nsew")

		self.show_frame("MenuScreen")

	def show_frame(self, page_name):
		frame = self.frames[page_name]
		frame.tkraise()

class MenuScreen(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		label = tk.Label(self, text="Menu", font=controller.title_font)
		label.pack(side="top", fill="x", pady=10)
		button1 = tk.Button(self, text="Go to Page One", command=lambda: controller.show_frame("Game"))
		button1.pack()

class Game(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller

		label = tk.Label(self, text="Game", font=controller.title_font)
		label.pack(side="top", fill="x", pady=10)
		button1 = tk.Button(self, text="Go Home", command=lambda: controller.show_frame("MenuScreen"))
		button2 = tk.Button(self, text="Start Normal", command=lambda: self.run_normal())
		button3 = tk.Button(self, text="Start Hex", command=lambda: self.run_hex())
		self.x_entry = tk.Entry(self)
		self.y_entry = tk.Entry(self)
		self.bombs_entry = tk.Entry(self)
		self.x_entry.pack()
		self.y_entry.pack()
		self.bombs_entry.pack()
		button1.pack()
		button2.pack()
		button3.pack()

	def run_normal(self):
		window = tk.Toplevel(self)
		x = int(self.x_entry.get())
		y = int(self.y_entry.get())
		bombs = int(self.bombs_entry.get())
		self.board = normal.Board(window, x, y, bombs)

	def run_hex(self):
		window = tk.Toplevel(self)
		x = int(self.x_entry.get())
		y = int(self.y_entry.get())
		bombs = int(self.bombs_entry.get())
		self.board = hex.Board(window, x, y, bombs)


if __name__ == "__main__":
	app = App()
	app.geometry("500x500")
	app.mainloop()
