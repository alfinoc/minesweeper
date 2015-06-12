from game import Player, Minesweeper

class Simulation:
   player = Player(game=Minesweeper(mines=100, width=30, height=30))
   score = 0

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
      return 'stop' not in response

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


sim = Simulation()
sim.auto()
sim.dump()


