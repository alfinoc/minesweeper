from math import factorial
from itertools import imap
from game import HIDDEN_VAL, MARKED_VAL

def quantify(pred, iterable):
   return sum(imap(pred, iterable))

# TODO: cache!
def nCr(n, r):
   if n < r:
      return 0
   elif n == r:
      return 1
   return factorial(n) / factorial(r) / factorial(n-r)

class FrozenList:
   def __init__(self, l, start=0):
      self.backing = list(l)
      self.start = start

   def head(self):
      if self.start >= len(self.backing):
         raise ValueError('no head to empty list!')
      return self.backing[self.start]

   def tail(self):
      return FrozenList(self.backing, self.start + 1)

   def next(self):
      if self.i >= len(self.backing):
         raise StopIteration()
      i = self.i
      self.i += 1
      return self.backing[i]

   def __iter__(self):
      self.i = self.start
      return self

   def __len__(self):
      return len(self.backing) - self.start

class Problem:
   def __init__(self, board, state):
      self.board = board
      self.full = state

      # Explore recursively through all hidden squares that we have information about.
      self.possibilities = FrozenList(self.consider(state))
      print list(self.possibilities)
      hidden = filter(lambda i : self.full[i] == HIDDEN_VAL, xrange(len(self.full)))
      self.noInfo = len(hidden) - len(self.possibilities)

      self.calls = 0

   def adjacent(self, index):
      return self.board.adjacent(index)

   def counts(self, left):
      return self.solve(left, list(self.full), self.possibilities)

   def consider(self, state):
      def hiddenWithInfo(i):
         return state[i] == HIDDEN_VAL and \
                any(state[neighbor] > 0 for neighbor in self.adjacent(i))
      return filter(hiddenWithInfo, xrange(len(state)))

   # Returns true iff all hints are 0.
   def complete(self, state):
      return any(val > 0 for val in state)

   # returns a pair (a,b) where a is the number of arrangements with a mine at a
   # and b is the number of arrangements with a mine not at a.

   # TODO: oh god i can't cache the way i think i can.
   # issue: the cache can't be just (mine at index, left) or (not, left) since
   # implicitly the arrangement of the board is changing as we go.
   # so this is terrible.
   def solve2(self, left, state, consider):
      self.calls += 1
      if left <= 0:
         return int(left == 0 and self.complete(state))
      if len(consider) == 0:
         possibilitiesLeft = quantify(lambda x : state[x] == HIDDEN_VAL, consider)
         return nCr(self.noInfo + possibilitiesLeft, left)

      else:
         position = consider.head()

         count = 0
         # Compute combinations with a mine here.
         if self.mark(position, state):
            count += self.solve(left - 1, state, consider.tail())
            self.unmark(position, state)

         # And with a mine not here.
         count += self.solve(left, state, consider.tail())
         #print 'count for {0} with {1} is {2}.'.format(i, left, count)
         return count

   def mark(self, i, state):
      adjacent = self.adjacent(i)
      for a in adjacent:
         # Illegal placement.
         if state[a] == 0:
            return False
      for a in adjacent:
         if state[a] > 0:
            state[a] -= 1
      return True

   def unmark(self, i, state):
      adjacent = self.adjacent(i)
      for a in adjacent:
         if state[a] >= 0:
            state[a] += 1
