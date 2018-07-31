# from tkinter import *
# root = Tk()
# image_button = PhotoImage(root, file="hexagonal_button.png")
# button_hex = Button(root, bg='white',border='0', image=image_button)
# button_hex.pack()
# root.mainloop()

import random
import sys
sys.setrecursionlimit(15000)
ii = 0
class Cell:
	def __init__(self, canv, x, y):
		self.bomb = False
		self.covered = True
		self.flag = False
		self.colour = "white"
		self.number = 0
		self.x = x
		self.y = y
		self.rec = canv.create_rectangle(24*x + 4, 24*y + 4, 24*x + 22, 24*y + 22, outline="#000", fill="#eee", tags="rec")
		self.text = canv.create_text(24*x + 13, 24*y + 13, fill="white",font="Times 20 italic bold", text="", tags="rec")


class Board:
	def __init__(self, root, size_x, size_y, bombs):
		self.canv = Canvas(root, width=24*size_x, height=24*size_y)
		self.size_x = size_x
		self.size_y = size_y
		self.flag_count = 0
		self.board = [[Cell(self.canv, x, y) for y in range(size_y)] for x in range(size_x)]
		self.canv.tag_bind('rec', '<ButtonPress-1>', self.onObjectLeftClick)
		self.canv.tag_bind('rec', '<ButtonPress-2>', self.onObjectRightClick)
		self.canv.pack()
		self.bombs = list()
		self.place_bombs(bombs)

	def onObjectLeftClick(self, event):
		print('Got object click', (event.x-4)//24, (event.y-4)//24)
		self.reveal((event.x-4)//24, (event.y-4)//24)
		print(event.widget.find_closest(event.x, event.y))

	def onObjectRightClick(self, event):
		print('Got object click', (event.x-4)//24, (event.y-4)//24)
		self.addFlag((event.x-4)//24, (event.y-4)//24)
		print(event.widget.find_closest(event.x, event.y))

	def check_game(self):
		for x,y in self.bombs:
			if not self.board[x][y].flag:
				return False
		if len(self.bombs) == self.flag_count:
			return True

	def place_bombs(self, bombs):
		for i in range(bombs):
			placed = False
			while (not placed):
				rand_x = random.randint(0, self.size_x-1)
				rand_y = random.randint(0, self.size_y-1)
				if not self.board[rand_x][rand_y].bomb:
					self.board[rand_x][rand_y].bomb = True
					self.bombs.append((rand_x, rand_y))
					for i in range(-1, 2):
						for j in range(-1, 2):
							if (i == 0 and j == 0):
								continue
							if (0 <= rand_x+i < self.size_x and 0 <= rand_y+j < self.size_y):
								self.board[rand_x+i][rand_y+j].number += 1
					placed = True

	def addFlag(self, x, y):
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
		if self.check_game():
			print("You Win...")
			self.canv.delete("all")
			self.canv.create_text(24*self.size_x//2, 24*self.size_y//2, fill="green",font="Times 20 italic bold", text="YOU WIN...")


	def reveal(self, x, y):
		if self.board[x][y].flag:
			return
		if self.board[x][y].bomb:
			print("GAMEOVER")
			self.canv.delete("all")
			self.canv.create_text(24*self.size_x//2, 24*self.size_y//2, fill="red",font="Times 20 italic bold", text="GAMEOVER")
		else:
			if self.board[x][y].covered:
				self.board[x][y].covered = False
				if self.board[x][y].number == 0:
					self.canv.itemconfig(self.board[x][y].rec, fill='white')
					for i in range(-1, 2):
						for j in range(-1, 2):
							if (i == 0 and j == 0):
								continue
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

from tkinter import *

print("Size x:\n")
x = int(input())
print("Size y:\n")
y = int(input())
print("Bombs:\n")
bombs = int(input())

root = Tk()
board = Board(root, x, y, bombs)
print(board.show_board())
root.mainloop()


# while True:
# 	print(board.show_board())
# 	print(board)
# 	print("Enter move (x, y)...\n")
# 	x = int(input())
# 	y = int(input())
# 	board.reveal(x, y)
