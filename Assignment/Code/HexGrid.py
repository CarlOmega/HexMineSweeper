import tkinter as tk
from tkinter import simpledialog
import time
import random
import math
import sqlite3

class Cell:
	def __init__(self, canv, x, y):
		self.bomb = False
		self.covered = True
		self.flag = False
		self.colour = "white"
		self.number = 0
		self.x = x
		self.y = y
		self.rec = canv.create_polygon(self.getPoints(), outline="#6C7A89", fill="#ABB7B7", tags="rec")
		if self.x%2 == 0:
			self.text = canv.create_text(24*self.x + 29, 24*self.y + 17, fill="white",font="Times 15 italic bold", text="", tags="rec")
		else:
			self.text = canv.create_text(24*self.x + 29, 24*self.y + 29, fill="white",font="Times 15 italic bold", text="", tags="rec")

	def getPoints(self):
		points = list()
		for i in range(6):
			angle_deg = 60 * i
			angle_rad = math.pi / 180 * angle_deg
			if self.x%2 == 0:
				points.append(24*self.x + 12 * math.cos(angle_rad) + 2 * 12 + 5)
				points.append(24*self.y + 12 * math.sin(angle_rad) + 17)
			else:
				points.append(24*self.x + 12 * math.cos(angle_rad) + 2 * 12 + 5)
				points.append(24*self.y + 12 * math.sin(angle_rad) + 2 * 12 + 5)
		return points


class Board:
	def __init__(self, root, size_x, size_y, bombs, time, database):
		self.window = root
		self.window.configure(background='#BDC3C7')
		self.canv = tk.Canvas(root, width=25*size_x, height=25*size_y, background='#BDC3C7', highlightbackground="green", highlightcolor="green")
		self.size_x = size_x
		self.size_y = size_y
		self.flag_count = 0

		self.database = database
		self.revealed = 0
		# timer setup
		self.time = time
		self.timer = tk.Label(root, text="", background='#BDC3C7')
		quitButton = tk.Button(root, text="Quit", background='#BDC3C7', command=lambda: self.quit())
		self.bomb_count = tk.Label(root, text="", background='#BDC3C7')
		quitButton.grid(row=0, column=1)
		self.timer.grid(row=0, column=2)
		self.bomb_count.grid(row=0, column=0)

		self.board = [[Cell(self.canv, x, y) for y in range(size_y)] for x in range(size_x)]
		self.canv.tag_bind('rec', '<ButtonPress-1>', self.onObjectLeftClick)
		self.canv.tag_bind('rec', '<ButtonPress-3>', self.onObjectRightClick)
		self.canv.grid(row=1, columnspan=3)
		self.bombs = list()
		self.place_bombs(bombs)
		self.bomb_count.configure(text="Bombs: " + str(len(self.bombs)))
		self.update_clock()

	def quit(self):
		self.window.destroy()

	def update_clock(self):
		self.timer.configure(text="Score: "+ str(self.time))
		if self.time > 0:
			self.time -= 1
			self.window.after(1000, self.update_clock)
		else:
			if not self.check_game():
				self.game_over("lose")

	def onObjectLeftClick(self, event):
		print('Got object click', (event.x-4)//24, (event.y-4)//24)
		item = event.widget.find_closest(event.x, event.y)
		print(item)
		x = (item[0]-1)//2//self.size_x
		y = (item[0]-1)//2%self.size_x
		print(x, y)
		self.reveal(x, y)
		if self.check_game():
			self.game_over("win")

	def onObjectRightClick(self, event):
		print('Got object click', (event.x-4)//24, (event.y-4)//24)
		item = event.widget.find_closest(event.x, event.y)
		print(item)
		x = (item[0]-1)//2//self.size_x
		y = (item[0]-1)//2%self.size_x
		print(x, y)
		self.add_flag(x, y)
		if self.check_game():
			self.game_over("win")

	def check_game(self):
		print(self.revealed, (self.size_x*self.size_y)-len(self.bombs))
		if self.revealed == (self.size_x*self.size_y)-len(self.bombs):
			return True
		for x,y in self.bombs:
			if not self.board[x][y].flag:
				return False
		if len(self.bombs) == self.flag_count:
			return True

	def game_over(self, status):
		if status == "lose":
			print("GAMEOVER")
			self.canv.delete("all")
			self.canv.create_text(24*self.size_x//2, 24*self.size_y//2, fill="red",font="Times 20 italic bold", text="GAMEOVER")
			self.time = 0
		elif status == "win":
			print("You Win...")
			self.canv.delete("all")
			self.canv.create_text(24*self.size_x//2, 24*self.size_y//2, fill="green",font="Times 20 italic bold", text="YOU WIN...")
			score = self.time
			self.time = 0
			name = simpledialog.askstring("Input", "What is your name?", parent=self.window)
			if name is not None:
				print("Storing score of: ", score, "By: ", name)
				c = self.database.cursor()
				c.execute("INSERT INTO scores VALUES (?, ?, ?, ?, ?, ?, ?)", ("hex", 1, name, self.size_x, self.size_y, len(self.bombs), score))
				self.database.commit()

	def place_bombs(self, bombs):
		for i in range(bombs):
			placed = False
			while (not placed):
				rand_x = random.randint(0, self.size_x-1)
				rand_y = random.randint(0, self.size_y-1)
				if not self.board[rand_x][rand_y].bomb:
					self.board[rand_x][rand_y].bomb = True
					self.bombs.append((rand_x, rand_y))
					if rand_x%2 == 0:
						for i,j in [(-1, -1), (-1, 0), (0, -1), (0, 1), (1, -1), (1, 0)]:
							if (0 <= rand_x+i < self.size_x and 0 <= rand_y+j < self.size_y):
								self.board[rand_x+i][rand_y+j].number += 1
					else:
						for i,j in [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)]:
							if (0 <= rand_x+i < self.size_x and 0 <= rand_y+j < self.size_y):
								self.board[rand_x+i][rand_y+j].number += 1
					placed = True

	def add_flag(self, x, y):
		if not self.board[x][y].covered:
			return
		if self.board[x][y].flag:
			self.board[x][y].flag = False
			self.flag_count -= 1
			self.canv.itemconfig(self.board[x][y].rec, fill='#eee')
			self.canv.itemconfig(self.board[x][y].text, text='')
		else:
			self.board[x][y].flag = True
			self.flag_count += 1
			self.canv.itemconfig(self.board[x][y].rec, fill='black')
			self.canv.itemconfig(self.board[x][y].text, text='F', fill='white')


	def reveal(self, x, y):
		if self.board[x][y].flag:
			return
		if self.board[x][y].bomb:
			self.game_over("lose")
			return
		else:
			if self.board[x][y].covered:
				self.board[x][y].covered = False
				self.revealed += 1
				if self.board[x][y].number == 0:
					self.canv.itemconfig(self.board[x][y].rec, fill='white')
					if x%2 == 0:
						for i,j in [(-1, -1), (-1, 0), (0, -1), (0, 1), (1, -1), (1, 0)]:
							if (0 <= x+i < self.size_x and 0 <= y+j < self.size_y):
								if self.board[x+i][y+j].covered:
									self.reveal(x+i, y+j)
					else:
						for i,j in [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)]:
							if (0 <= x+i < self.size_x and 0 <= y+j < self.size_y):
								if self.board[x+i][y+j].covered:
									self.reveal(x+i, y+j)
				elif self.board[x][y].number == 1:
					self.canv.itemconfig(self.board[x][y].rec, fill='blue')
					self.canv.itemconfig(self.board[x][y].text, text=str(self.board[x][y].number), fill='black')
				elif self.board[x][y].number == 2:
					self.canv.itemconfig(self.board[x][y].rec, fill='yellow')
					self.canv.itemconfig(self.board[x][y].text, text=str(self.board[x][y].number), fill='black')
				elif self.board[x][y].number == 3:
					self.canv.itemconfig(self.board[x][y].rec, fill='red')
					self.canv.itemconfig(self.board[x][y].text, text=str(self.board[x][y].number), fill='black')
				elif self.board[x][y].number > 3:
					self.canv.itemconfig(self.board[x][y].rec, fill='darkred')
					self.canv.itemconfig(self.board[x][y].text, text=str(self.board[x][y].number), fill='black')
			else:
				return

	def show_board(self):
		output = ""
		for y in range(self.size_y):
			for x in range(self.size_x):
				if self.board[x][y].bomb:
					output += "|B|"
				else:
					if self.board[x][y].number > 0:
						output += "|"+ str(self.board[x][y].number) +"|"
					else:
						output += "| |"
			output += "\n"
		return output

	def __str__(self):
		output = ""
		for y in range(self.size_y):
			for x in range(self.size_x):
				if not self.board[x][y].covered:
					if self.board[x][y].bomb:
						output += "|B|"
					else:
						if self.board[x][y].number > 0:
							output += "|"+ str(self.board[x][y].number) +"|"
						else:
							output += "| |"
				else:
					output += "|█|"
			output += "\n"
		return output
