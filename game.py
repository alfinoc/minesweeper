from random import shuffle
from BashColor import BashColor as color

MINE_VAL = -1
HIDDEN_VAL = -2
MARKED_VAL = -3

DISPLAY = {
   MINE_VAL: color.Red('X'),
   HIDDEN_VAL: color.DarkGray(' '),
   MARKED_VAL: color.LightRed('!'),
   0: color.DarkGray('_')
}

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
      return DISPLAY[hint] if hint in DISPLAY else color[toColor(hint)](str(hint))

   def dump(self, hideMask=None, markMask=None):
      masked = self.masked(hideMask, markMask)
      display = lambda index : masked[index]
      for i in range(0, self.height):
         indices = range(i * self.width, (i + 1) * self.width)
         print ' '.join(map(self.format, map(display, indices)))

   def masked(self, hideMask, markMask):
      def apply(original, mask, replace):
         indices = range(len(original))
         swap = lambda i : replace if mask != None and mask[i] else original[i]
         return map(swap, indices)

      res = apply(self.grid, hideMask, HIDDEN_VAL)
      res = apply(res, markMask, MARKED_VAL)
      return res

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
      self.hidden = [True] * len(self.board.grid)

   # returns True if hit mine, False otherwise
   def reveal(self, x, y):
      index = self.board.toIndex(x, y)
      if not self.hidden[index]:
         return False
      self.hidden[index] = False
      hit = self.board.hint(x, y)
      if hit == MINE_VAL:
         return True
      elif hit == 0:
         for i, j in self.board.adjacent(x, y):
            self.reveal(i, j)
         return False

   def dump(self, markMask=None):
      self.board.dump(hideMask=self.hidden, markMask=markMask)
   
   def dimensions(self):
      return (self.board.width, self.board.height)

class Player:
   def __init__(self, game=Minesweeper()):
      self.game = game
      self.errors = 0
      self.marked = [False] * len(self.game.hidden)

   def mark(self, x, y):
      self.marked[self.game.board.toIndex(x, y)] = True

   def dump(self):
      self.game.dump(self.marked)

   def reveal(self, x, y):
      self.game.reveal(x, y)




