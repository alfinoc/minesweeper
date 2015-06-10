from game import Minesweeper

g = Minesweeper()
g.dump()

while True:
   try:
      guess = map(int, raw_input('hit me: ').split())
      if len(guess) == 1:
         x, y = g.board.toCoordinates(guess[0])
      else:
         x, y = guess
   except:
      print 'bad format, man'
      continue
   if x == -1:
      break
   g.reveal(x, y)
   g.dump()