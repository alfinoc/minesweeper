from random import shuffle, choice
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

   def hint(self, i):
      return self.grid[i]

   def _computeHint(self, index):
      if self.grid[index] == MINE_VAL:
         return MINE_VAL
      else:
         x, y = self.toCoordinates(index)
         adjacent = 0
         for i in self.adjacent(index):
            adjacent += int(self.grid[i] == MINE_VAL)
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

   def adjacent(self, i):
      x, y = self.toCoordinates(i)
      pairs = []
      for i in range(max(0, x - 1), min(x + 2, self.width)):
         for j in range(max(0, y - 1), min(y + 2, self.height)):
            pairs.append((i, j))
      return map(lambda p : self.toIndex(*p), pairs)

   def toIndex(self, x, y):
      return x + y * self.width

   def toCoordinates(self, i):
      return (i % self.width, i / self.width)

class Minesweeper:
   def __init__(self, mines=100, width=30, height=30):
      self.board = Board(mines, width, height)
      self.hidden = [True] * len(self.board.grid)

   # returns True if hit mine, False otherwise
   def reveal(self, i):
      if not self.hidden[i]:
         return False
      self.hidden[i] = False
      hit = self.board.hint(i)
      if hit == MINE_VAL:
         return True
      elif hit == 0:
         for j in self.board.adjacent(i):
            self.reveal(j)
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

   def mark(self, i):
      self.marked[i] = True

   def dump(self):
      self.game.dump(self.marked)

   def reveal(self, i):
      return self.game.reveal(i)

   def state(self):
      return self.game.board.masked(self.game.hidden, self.marked)

   # returns true if anything was successfully flagged, false otherwise
   def sweep(self):
      toMark = []

      state = self.state()
      indices = range(len(self.marked))
      for i in indices:
         hint = state[i]

         # Only consider useful hints.
         if hint <= 0:
            continue

         #x, y = self.game.board.toCoordinates(i)
         #index = lambda pair : self.game.board.toIndex(*pair)
         adjacent = self.game.board.adjacent(i)
         marked = filter(lambda j : state[j] == MARKED_VAL, adjacent)
         unknown = filter(lambda j : state[j] == HIDDEN_VAL, adjacent)

         if len(unknown) == hint - len(marked):
            for j in unknown:
               toMark.append(j)

      for i in toMark:
         self.mark(i)
      return len(toMark) != 0

   def eliminate(self):
      toMark = []

      state = self.state()
      indices = range(len(self.marked))
      for i in indices:
         hint = state[i]

         # Only consider useful hints.
         if hint <= 0:
            continue

         #x, y = self.game.board.toCoordinates(i)
         #index = lambda pair : self.game.board.toIndex(*pair)
         adjacent = self.game.board.adjacent(index)
         marked = filter(lambda j : state[j] == MARKED_VAL, adjacent)
         unknown = filter(lambda j : state[j] == HIDDEN_VAL, adjacent)

         if hint - len(marked) == 0:
            for j in unknown:
               toMark.append(j)

      for i in toMark:
         self.reveal(i)
      return len(toMark) != 0

   def guess(self):
      state = self.state()
      indices = range(len(self.marked))
      unknown = filter(lambda i : state[i] == HIDDEN_VAL, indices)
      randomGuess = choice(unknown)
      return self.reveal(randomGuess)
