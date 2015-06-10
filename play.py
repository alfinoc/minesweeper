from game import Player

class Simulation:
   player = Player()
   score = 0

   def sweep(self):
      while self.player.sweep():
         print 'Sweeping...'

   def guess(self):
      print 'Guessing...'
      self.score += int(self.player.guess())

   def dump(self):
      self.player.dump()
      print 'mines hit: {0}'.format(self.score)

   def prompt(self):
      response = raw_input('')
      if 's' in response:
         self.sweep()
      elif 'g' in response:
         self.guess()
      elif 'b' in response:  # 'b' for both
         self.sweep()
         self.guess()
      return 'stop' not in response


sim = Simulation()
while sim.prompt():
   sim.dump()
