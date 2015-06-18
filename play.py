from game import Player, Minesweeper
from guessing import Problem

identity = lambda x : x

class Simulation:
   def __init__(self):
      mines = 3
      self.player = Player(game=Minesweeper(mines=mines, width=5, height=5))
      self.score = 0
      self.undiscovered = mines

   def minesLeft(self):
      return self.undiscovered - self.score - len(filter(identity, self.player.marked))

   def sweep(self):
      while self.player.sweep(): pass

   def guess(self):
      self.score += int(self.player.guess())

   def dump(self):
      self.player.dump()
      print 'mines hit:', str(self.score)

   def prompt(self):
      response = raw_input('')
      if 's' in response:
         self.sweep()
      elif 'g' in response:
         self.guess()
      elif 'e' in response:
         self.player.eliminate()
      elif 'b' in response:  # 'b' for both
         self.sweep()
         self.guess()
      return 'stop' not in response and not self.player.complete()

   def auto(self, interval=0, verbose=False):
      while not self.player.complete():
         progress = True
         while progress:
            progress = False
            if verbose: print 'Sweeping...'
            progress = progress or self.sweep()
            if verbose: print 'Eliminating...'
            progress = progress or self.player.eliminate()
         if verbose: print 'Guessing...'
         self.guess()
      print 'final score:', str(self.score)

   def manual(self):
      while self.prompt():
         self.dump()

   def probabilities(self):
      prob = Problem(self.player.game.board, self.player.state())
      return prob.probabilities(self.minesLeft())

   def s(self):
      self.guess()
      self.dump()

sim = Simulation()

#sim.auto()
#sim.dump()


