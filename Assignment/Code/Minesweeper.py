import tkinter as tk
from tkinter import font as tkfont
import random
import sys
import NormalGrid as normal
import HexGrid as hex
import sqlite3
sys.setrecursionlimit(15000)

class App(tk.Tk):
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
		self.database = sqlite3.connect('highscores.db')

		container = tk.Frame(self)
		container.pack(side="top", fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)
		# Setup the pages to switch between
		self.frames = {}
		for F in (MenuScreen, Game, Highscores):
			page_name = F.__name__
			frame = F(parent=container, controller=self, database=self.database)
			self.frames[page_name] = frame
			frame.grid(row=0, column=0, sticky="nsew")

		self.show_frame("MenuScreen")

	def show_frame(self, page_name):
		if page_name == "Highscores":
			self.frames[page_name].load_highscores()
		frame = self.frames[page_name]
		frame.tkraise()

	def quit(self):
		exit()

class MenuScreen(tk.Frame):
	def __init__(self, parent, controller, database):
		tk.Frame.__init__(self, parent, background='#BDC3C7')
		self.controller = controller
		self.database = database
		label = tk.Label(self, text="Menu", font=controller.title_font, background='#BDC3C7')
		highscores_button = tk.Button(self, text="High Scores", command=lambda: controller.show_frame("Highscores"), height=2, width=40, background="#6C7A89")
		quit_button = tk.Button(self, text="Quit", command=lambda: controller.quit(), height=2, width=40, background="#6C7A89")
		play_button = tk.Button(self, text="Play", command=lambda: controller.show_frame("Game"), height=2, width=40, background="#6C7A89")

		label.pack(side="top", fill="x", pady=10)
		play_button.pack()
		highscores_button.pack()
		quit_button.pack()

class Highscores(tk.Frame):
	def __init__(self, parent, controller, database):
		tk.Frame.__init__(self, parent, background='#BDC3C7')
		self.controller = controller
		self.database = database
		label = tk.Label(self, text="High Scores", font=controller.title_font, background='#BDC3C7')
		home_button = tk.Button(self, text="Go Home", command=lambda: controller.show_frame("MenuScreen"), height=2, width=40, background="#6C7A89")

		self.listbox = tk.Listbox(self, width=100)
		label.pack(side="top", fill="x", pady=10)
		home_button.pack()

		self.listbox.pack()

	def load_highscores(self):
		self.listbox.delete(0, tk.END)
		c = self.database.cursor()
		for b in c.execute('SELECT * FROM scores'):
			self.listbox.insert(tk.END, b)


class Game(tk.Frame):
	def __init__(self, parent, controller, database):
		tk.Frame.__init__(self, parent, background='#BDC3C7')
		self.winfo_toplevel().title("Minesweeper")
		self.controller = controller
		self.database = database

		label = tk.Label(self, text="Game", font=controller.title_font, background='#BDC3C7')
		home_button = tk.Button(self, text="Go Home", command=lambda: controller.show_frame("MenuScreen"), height=2, width=40, background="#6C7A89")
		normal_button = tk.Button(self, text="Start Normal", command=lambda: self.run_normal(), height=2, width=40, background="#6C7A89")
		hex_button = tk.Button(self, text="Start Hex", command=lambda: self.run_hex(), height=2, width=40, background="#6C7A89")

		self.level_choice = tk.StringVar(self)
		self.levels = ['Easy', 'Medium', 'Hard', 'Super Hard']
		self.level_choice.set('Easy')
		self.level_selector = tk.OptionMenu(self, self.level_choice, *self.levels)
		self.level_selector.configure(width=40, background="#6C7A89", highlightbackground="green", highlightcolor="green")
		level_label = tk.Label(self, text="Select Level", background='#BDC3C7')


		label.pack(side="top", fill="x", pady=10)
		home_button.pack()
		level_label.pack()
		self.level_selector.pack()
		normal_button.pack()
		hex_button.pack()

	def run_normal(self):
		window = tk.Toplevel(self)
		window.winfo_toplevel().title("Normal Minesweeper")
		option = self.level_choice.get()
		if (option == 'Easy'):
			x = 10
			y = 10
			bombs = 8
			time = 120
		elif (option == 'Medium'):
			x = 20
			y = 20
			bombs = 30
			time = 300
		elif (option == 'Hard'):
			x = 30
			y = 30
			bombs = 100
			time = 600
		elif (option == 'Super Hard'):
			x = 30
			y = 30
			bombs = 200
			time = 600
		self.normal_board = normal.Board(window, x, y, bombs, time, self.database)

	def run_hex(self):
		window = tk.Toplevel(self)
		window.winfo_toplevel().title("Normal Minesweeper")
		option = self.level_choice.get()
		if (option == 'Easy'):
			x = 15
			y = 15
			bombs = 10
			time = 120
		elif (option == 'Medium'):
			x = 20
			y = 20
			bombs = 30
			time = 300
		elif (option == 'Hard'):
			x = 30
			y = 30
			bombs = 100
			time = 600
		elif (option == 'Super Hard'):
			x = 30
			y = 30
			bombs = 200
			time = 600
		self.hex_board = hex.Board(window, x, y, bombs, time, self.database)


if __name__ == "__main__":
	app = App()
	app.geometry("500x500")
	app.mainloop()
