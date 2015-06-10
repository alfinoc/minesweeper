from game import Player

p = Player()
p.dump()

while True:
   try:
      action = p.reveal if 'r' in raw_input('what: ') else p.mark
      guess = map(int, raw_input('where: ').split())
      if len(guess) == 1:
         x, y = g.board.toCoordinates(guess[0])
      else:
         x, y = guess
   except:
      print 'bad format, man'
      continue
   if x == -1:
      break
   action(x, y)
   p.dump()
