from random import shuffle, choice
from functools import partial
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

def cached(fn):
   cache = {}
   def checkCache(*args):
      if args in cache:
         return cache[args]
      else:
         res = fn(*args)
         cache[args] = res
         return res
   return checkCache

def toColor(count):
   choices = ['DarkGray', 'Blue', 'Green', 'Magenta', 'Yellow', 'White']
   return choices[min(count, len(choices) - 1)]

class Board:
   def __init__(self, mines=3, width=4, height=6):
      self.adjacent = cached(self._adjacent)
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
      for i in xrange(0, self.height):
         indices = xrange(i * self.width, (i + 1) * self.width)
         print ' '.join(map(self.format, map(display, indices)))

   def masked(self, hideMask, markMask):
      def apply(original, mask, replace):
         indices = xrange(len(original))
         swap = lambda i : replace if mask != None and mask[i] else original[i]
         return map(swap, indices)

      res = apply(self.grid, hideMask, HIDDEN_VAL)
      res = apply(res, markMask, MARKED_VAL)
      return res

   # Cached into public 'Board.adjacent'.
   def _adjacent(self, index):
      x, y = self.toCoordinates(index)
      pairs = []
      for i in xrange(max(0, x - 1), min(x + 2, self.width)):
         for j in xrange(max(0, y - 1), min(y + 2, self.height)):
            if (i, j) != (x, y):
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

   def complete(self):
      def mismatched(mark, hide, val):
         return hide and ((val == MINE_VAL) != mark)
      full = zip(self.marked, self.game.hidden, self.game.board.grid)
      return len(filter(lambda t : mismatched(*t), full)) == 0

   def mark(self, i, check=False):
      if check and self.game.board.grid[i] != MINE_VAL:
         raise ValueError('Marked a non-mine!')
      self.marked[i] = True

   def dump(self):
      self.game.dump(self.marked)

   def reveal(self, i):
      return self.game.reveal(i)

   def state(self):
      return self.game.board.masked(self.game.hidden, self.marked)

   def sweep(self):
      def mines(hint, adjacent, marked, unknown):
         return unknown if len(unknown) == hint - len(marked) else []
      return self.infer(mines, partial(self.mark, check=True))

   def eliminate(self):
      def safe(hint, adjacent, marked, unknown):
         return unknown if hint - len(marked) == 0 else []
      return self.infer(safe, self.reveal)

   # applies 'applyFn' to every index returned by selectFn when passed
   # (hint, adjacent, marked, unknown) for every informative hint on the
   # board. 'applyFn' is only called after all 'selectFn' calls have been
   # completed. returns true if anything was applied, false otherwise.
   def infer(self, selectFn, applyFn):
      matching = []

      state = self.state()
      for i in xrange(len(self.marked)):
         hint = state[i]

         # Only consider useful hints that are known.
         if hint <= 0:
            continue

         adjacent = self.game.board.adjacent(i)

         marked = filter(lambda j : state[j] == MARKED_VAL or
                                    state[j] == MINE_VAL, adjacent)
         unknown = filter(lambda j : state[j] == HIDDEN_VAL, adjacent)

         matching.extend(selectFn(hint, adjacent, marked, unknown))

      for i in matching:
         applyFn(i)
      return len(matching) != 0

   def guess(self):
      state = self.state()
      indices = xrange(len(self.marked))
      unknown = filter(lambda i : state[i] == HIDDEN_VAL, indices)
      if len(unknown) == 0:
         return False
      return self.reveal(choice(unknown))
