Game = {};
Color = {}

Game.MINE_VAL = MINE_VAL = -1
Game.HIDDEN_VAL = HIDDEN_VAL = -2
Game.MARKED_VAL = MARKED_VAL = -3

Color.Red = Color.DarkGray = Color.LightRed = Color.Blue = Color.Green
          = Color.Magenta = Color.Yellow = Color.White = function(s) {
   return s;
}

Game.DISPLAY = {
   MINE_VAL: Color.Red('X'),
   HIDDEN_VAL: Color.DarkGray(' '),
   MARKED_VAL: Color.LightRed('!'),
   0: Color.DarkGray('_')
}

function toColor(count) {
   choices = ['DarkGray', 'Blue', 'Green', 'Magenta', 'Yellow', 'White']
   return choices[Math.min(count, choices.length - 1)]
}

function len(a) {
   return a.length;
}

function int(s) {
   return parseInt(s);  
}

function map(fn, array) {
   return array.map(fn);
}

None = undefined;

function shuffle(array) {
  var currentIndex = array.length, temporaryValue, randomIndex ;
  while (0 !== currentIndex) {
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex -= 1;

    temporaryValue = array[currentIndex];
    array[currentIndex] = array[randomIndex];
    array[randomIndex] = temporaryValue;
  }

  return array;
}

range = xrange = function(low, hi) {
   var res = [];
   for (var i = low; i < hi; i++) {
      res.push(i);
   }
   return res;
};

Game.init = function(mines, width, height) {
   Game.width = width;
   Game.height = height;
   Game.grid = [];
   for (var i = 0; i < mines; i++)
      Game.grid.push(Game.MINE_VAL);
   for (var i = 0; i < width * height - mines; i++)
      Game.grid.push(0);
   shuffle(Game.grid);
   Game.grid = map(Game._computeHint, range(0, len(Game.grid)));
}

Game.hint = function(i) {
   return Game.grid[i];
}

Game._computeHint = function(index) {
   if (Game.grid[index] == Game.MINE_VAL) {
      return Game.MINE_VAL;
   } else {
      var pair = Game.toCoordinates(index);
      var x = pair[0];
      var y = pair[1];
      var adjacent = 0;
      Game.adjacent(index).forEach(function(i) {
         adjacent += Game.grid[i] == Game.MINE_VAL ? 1 : 0;
      });
      return adjacent;
   }
};

Game.format = function(hint) {
   return hint;
   // TODO: Color solution.
   //return Game.DISPLAY[hint] if hint in Game.DISPLAY else Color[toColor(hint)](str(hint))
};

Game.dump = function(hideMask, markMask) {
   var masked = Game.masked(hideMask, markMask)
   var display = function(index) { return masked[index]; };
   for (var i = 0; i < Game.height; i++) {
      indices = xrange(i * Game.width, (i + 1) * Game.width)
      console.log(map(Game.format, map(display, indices)).join(' '));
   }
};

Game.masked = function(hideMask, markMask) {
   function apply(original, mask, replace) {
      var indices = xrange(0, len(original));
      function swap(i) {
         return mask != None && mask[i] ? replace : original[i];
      }
      return map(swap, indices);
   }

   var res = apply(Game.grid, hideMask, Game.HIDDEN_VAL)
   res = apply(res, markMask, Game.MARKED_VAL)
   return res;
};

Game.adjacent = function(index) {
   var pair = Game.toCoordinates(index);
   var x = pair[0];
   var y = pair[1];
   var pairs = [];
   for (var i = Math.max(0, x - 1); i < Math.min(x + 2, Game.width); i++)
      for (var j = Math.max(0, y - 1); j < Math.min(y + 2, Game.height); j++)
         if (!(i == x && j == y))
            pairs.push([i, j]);
   return map(Game.toIndex, pairs);
}

Game.toIndex = function(pair) {
   return pair[0] + pair[1] * Game.width
}

Game.toCoordinates = function(i) {
   return [i % Game.width, int(i / Game.width)];
}



