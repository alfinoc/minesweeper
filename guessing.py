from itertools import imap
from game import HIDDEN_VAL, MARKED_VAL

def quantify(iterable, pred=bool):
   return sum(imap(pred, iterable))

class FrozenList:
   def __init__(self, l, start=0):
      self.backing = l
      self.start = start

   def tail(self, start):
      return FrozenList(self.backing, start)

   def next(self):
      if self.i >= len(self.backing):
         raise StopIteration()
      i = self.i
      self.i += 1
      return i

   def __iter__(self):
      self.i = self.start
      return self

   def __len__(self):
      return len(self.backing) - self.start

class Problem:
   def __init__(self, board, state):
      self.board = board
      self.full = state

   def adjacent(self, index):
      return self.board.adjacent(index)

   def probabilities(self, left):
      consider = filter(lambda i : self.full[i] != HIDDEN_VAL, xrange(len(self.full)))
      self.solve(left, list(self.full), FrozenList(consider))

   def consider(self, state):
      def hasInfo(i):
         return any(neighbor > 0 for neighbor in self.adjacent(i))
      return filter(hasInfo, xrange(len(state)))

   # Returns true iff all hints are 0.
   def complete(self, state):
      return any(val > 0 for val in state)

   def solve(self, left, state, consider):
      if left <= 0:
         return int(left == 0 and self.complete(state))
      if len(consider) == 0:
         return left <= quantify(consider, pred=(lambda x : state[x] == HIDDEN_VAL))
      else:
         count = 0
         for i in consider:
            # First mark.
            if self.mark(i, state):
               count += self.solve(left - 1, state, consider.tail(i + 1))
               self.unmark(i, state)
            # Then don't.
            count += self.solve(left, state, consider.tail(i + 1))
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
         state[a] += 1
