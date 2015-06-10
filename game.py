from random import shuffle
from BashColor import BashColor as color

MINE_VAL = None
MINE_DISPLAY = 'X'
EMPTY_DISPLAY = '_'
HIDDEN_VAL = -1
HIDDEN_DISPLAY = '?'

def toColor(count):
   choices = ['DarkGray', 'Blue', 'Green', 'Magenta', 'Yellow', 'White']
   return choices[min(count, len(choices) - 1)]

class Board:
   def __init__(self, mines=3, width=4, height=6):
      self.width = width
      self.height = height
      self.grid = [MINE_VAL] * mines + [0] * (width * height - mines)
      shuffle(self.grid)
      self.grid = map(self._computeHint, range(len(self.grid)))

   def hint(self, x, y):
      return self.grid[y * self.width + x]

   def _computeHint(self, index):
      if self.grid[index] == MINE_VAL:
         return MINE_VAL
      else:
         x, y = self.toCoordinates(index)
         adjacent = 0
         for i, j in self.adjacent(x, y):
            adjacent += int(self.grid[self.toIndex(i, j)] == MINE_VAL)
         return adjacent

   def format(self, hint):
      if hint == MINE_VAL:
         return color.Red(MINE_DISPLAY)
      elif hint == 0:
         return color.DarkGray(EMPTY_DISPLAY)
      else:
         return color[toColor(hint)](str(hint))

   def dump(self, mask=None):
      for i in range(0, self.height):
         indices = range(i * self.width, (i + 1) * self.width)
         def hint(index):
            if mask == None or mask[index]:
               return self.grid[index]
            else:
               return HIDDEN_DISPLAY
         print ' '.join(map(self.format, map(hint, indices)))

   def adjacent(self, x, y):
      pairs = []
      for i in range(max(0, x - 1), min(x + 2, self.width)):
         for j in range(max(0, y - 1), min(y + 2, self.height)):
            pairs.append((i, j))
      return pairs

   def toIndex(self, x, y):
      return x + y * self.width

   def toCoordinates(self, i):
      return (i % self.width, i / self.width)

class Minesweeper:
   def __init__(self, mines=100, width=30, height=30):
      self.board = Board(mines, width, height)
      self.revealed = [False] * len(self.board.grid)

   # returns True if hit mine, False otherwise
   def reveal(self, x, y):
      index = self.board.toIndex(x, y)
      if self.revealed[index]:
         return False
      self.revealed[index] = True
      hit = self.board.hint(x, y)
      if hit == MINE_VAL:
         return True
      elif hit == 0:
         for i, j in self.board.adjacent(x, y):
            self.reveal(i, j)
         return False

   def dump(self):
      self.board.dump(mask=self.revealed)
      











