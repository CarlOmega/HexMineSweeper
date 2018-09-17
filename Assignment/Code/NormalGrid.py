import tkinter as tk
from tkinter import simpledialog
import time
import random
import sqlite3

class Cell:
	"""Cell stores the relevant information about each cell tile.

   Attributes:
	   bomb (bool): Stores if the cell contains a bomb.
	   covered (bool): Stores if the cell if revealed or covered from user.
	   flag (bool): Stores if the cell if marked with a flag.
	   colour (str): The colour of the tile.
	   number (int): The number of neighbouring bombs.
	   x (int): x coordinate ID used for drawing reletive.
	   y (int): y coordinate ID used for drawing reletive.
	   rec (Rectangle): Canvas Rectangle used in drawing.
	   text (Text): Canvas Text used in drawing number of neighbouring bombs.

   """
	def __init__(self, canv, x, y):
		"""Cell Setup call.

        The default setup is that there is no bomb, the cell is covered and there
		is no flag. Also the colour is default white and x, y coordinates are set.
		The drawing objects are also created at this point.

        Args:
            canv (Canvas): The canvas the cell should be drawn on.
            x (int): x coordinate.
            y (int): y coordinate.

        """
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
	"""Board stores references to all the Cells and has functions to play the game.

   Attributes:
	   canv (Canvas): The canvas the board should be drawn onto.
	   size_x (int): The size of how many cells there should be in a column.
	   size_y (int): The size of how many cells there should be in a row.
	   flag_count (int): How many flags are on the board.
	   board (Cell[][]): The 2D array to store the cells.
	   bombs ((int, int)[]): x and y coordinates of the bombs locations.

   """
	def __init__(self, root, size_x, size_y, bombs, database):
		"""Board setup.

        This setup just creates the board then sets random cells to contain bombs.

        Args:
            root (Panel): Where the Canvas should be created.
            size_x (int): The size of how many cells there should be in a column.
			size_y (int): The size of how many cells there should be in a row.
            bombs (int): Amount of bombs to be placed.

        """
		self.window = root
		self.canv = tk.Canvas(root, width=24*size_x, height=24*size_y)
		self.size_x = size_x
		self.size_y = size_y
		self.flag_count = 0

		self.database = database
		self.revealed = 0
		# timer setup
		self.time = ((size_x*size_y)//100)*bombs
		self.timer = tk.Label(root, text="")
		self.timer.pack()
		quitButton = tk.Button(root, text="Quit", command=lambda: self.quit())
		quitButton.pack()

		self.board = [[Cell(self.canv, x, y) for y in range(size_y)] for x in range(size_x)]
		self.canv.tag_bind('rec', '<ButtonPress-1>', self.onObjectLeftClick)
		self.canv.tag_bind('rec', '<ButtonPress-3>', self.onObjectRightClick)
		self.canv.pack()
		self.bombs = list()
		self.place_bombs(bombs)
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
		"""Left click event onto a cell.

		Handles the event of clicking onto a cell.

        Args:
            event (Event): Details of the event that triggered.
        """
		print('Got object click', (event.x-4)//24, (event.y-4)//24)
		self.reveal((event.x-4)//24, (event.y-4)//24)
		print(event.widget.find_closest(event.x, event.y))
		if self.check_game():
			self.game_over("win")

	def onObjectRightClick(self, event):
		"""Right click event onto a cell.

		Handles the event of right clicking onto a cell.

        Args:
            event (Event): Details of the event that triggered.
        """
		print('Got object click', (event.x-4)//24, (event.y-4)//24)
		self.addFlag((event.x-4)//24, (event.y-4)//24)
		print(event.widget.find_closest(event.x, event.y))
		if self.check_game():
			self.game_over("win")

	def check_game(self):
		"""Checks if game state is complete.

		Checks list of bombs to see if they have been flagged, and also checks
		there isnt any extra flags.

        Returns:
            True if complete, False otherwise.
        """
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
				c.execute("INSERT INTO scores VALUES (?, ?, ?, ?, ?, ?, ?)", ("normal", 1, name, self.size_x, self.size_y, self.bombs, score))
				self.database.commit()


	def place_bombs(self, bombs):
		"""Places bombs on random cells.

        Randomly picks new spots to place bombs.

        Args:
            bombs (int): amount of bombs to place
        """
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
		"""Adds a flag to the relevant Cell.

		Adds a flag to the cell then updates the drawing, after then checks
		gamestate to see if the user won.

        Args:
            x (int): x coordinate of Cell targeted.
			y (int): y coordinate of Cell targeted.
        """
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
		"""Recursive method to reveal Cells.

        Recursively reaveals a cell then if that cell has 0 neighbouring bombs
		it calls the Recursive method on each neighbour that isnt revealed.

        Args:
            x (int): x coordinate of Cell to be revealed.
			y (int): y coordinate of Cell to be revealed.

        """
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
		"""Shows board state for debugging.

		Returns:
			output (str): Board view.
        """
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
