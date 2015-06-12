TABLE_SELECTOR = '#grid'

Color = {};

Color.toColor = function(count) {
   choices = ['gray', 'blue', 'green', 'magenta', 'yellow', 'white']
   return choices[Math.min(count, choices.length - 1)]
};

Board = {};

Board.MINE_VAL = -1
Board.HIDDEN_VAL = -2
Board.MARKED_VAL = -3

Board.DISPLAY = {};
Board.DISPLAY[Board.MINE_VAL] = ['red', 'X'];
Board.DISPLAY[Board.HIDDEN_VAL] = ['gray', '?'];
Board.DISPLAY[Board.MARKED_VAL] = ['pink', '!'];
Board.DISPLAY[0] = ['gray', '_'];

function len(a) {
   return a.length;
}

function int(s) {
   return parseInt(s);  
}

function map(fn, array) {
   return array.map(fn);
}

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

var range = xrange = function(low, hi) {
   var res = [];
   for (var i = low; i < hi; i++) {
      res.push(i);
   }
   return res;
};

Board.init = function(mines, width, height) {
   Board.width = width;
   Board.height = height;
   Board.grid = [];
   for (var i = 0; i < mines; i++)
      Board.grid.push(Board.MINE_VAL);
   for (var i = 0; i < width * height - mines; i++)
      Board.grid.push(0);
   shuffle(Board.grid);
   Board.grid = map(Board._computeHint, range(0, len(Board.grid)));
}

Board.hint = function(i) {
   return Board.grid[i];
}

Board._computeHint = function(index) {
   if (Board.grid[index] == Board.MINE_VAL) {
      return Board.MINE_VAL;
   } else {
      var pair = Board.toCoordinates(index);
      var x = pair[0];
      var y = pair[1];
      var adjacent = 0;
      Board.adjacent(index).forEach(function(i) {
         adjacent += Board.grid[i] == Board.MINE_VAL ? 1 : 0;
      });
      return adjacent;
   }
};

Board.format = function(index, hint) {
   hint = parseInt(hint);
   var d = Board.DISPLAY[hint];
   var color, character;
   if (d) {
      color = d[0];
      character = d[1];
   } else {
      color = Color.toColor(hint);
      character = hint;
   }

   return '<td color="' + color + '" index="' + index + '">' + character + '</td>';
};

Board.dump = function(hideMask, markMask) {
   var parent = document.querySelector(TABLE_SELECTOR);
   var masked = Board.masked(hideMask, markMask)
   var display = function(index) { return masked[index]; };
   parent.innerHTML = '';
   for (var i = 0; i < Board.height; i++) {
      var row = '<tr>';
      for (var j = 0; j < Board.width; j++) {
         var index = j + i * Board.width;
         row += Board.format(index, masked[index]);
      }
      parent.innerHTML += row + '</tr>';
   }
};

Board.masked = function(hideMask, markMask) {
   function apply(original, mask, replace) {
      var indices = xrange(0, len(original));
      function swap(i) {
         return mask != undefined && mask[i] ? replace : original[i];
      }
      return map(swap, indices);
   }

   var res = apply(Board.grid, hideMask, Board.HIDDEN_VAL)
   res = apply(res, markMask, Board.MARKED_VAL)
   return res;
};

Board.adjacent = function(index) {
   var pair = Board.toCoordinates(index);
   var x = pair[0];
   var y = pair[1];
   var pairs = [];
   for (var i = Math.max(0, x - 1); i < Math.min(x + 2, Board.width); i++)
      for (var j = Math.max(0, y - 1); j < Math.min(y + 2, Board.height); j++)
         if (!(i == x && j == y))
            pairs.push([i, j]);
   return map(Board.toIndex, pairs);
}

Board.toIndex = function(pair) {
   return pair[0] + pair[1] * Board.width
}

Board.toCoordinates = function(i) {
   return [i % Board.width, int(i / Board.width)];
};

Minesweeper = {};

Minesweeper.init = function(mines, width, height) {
   Board.init(mines, width, height);
   Minesweeper.hidden = []
   for (var i = 0; i < len(Board.grid); i++) {
      Minesweeper.hidden.push(true);
   }
};

Minesweeper.reveal = function(i) {
   if (!Minesweeper.hidden[i]) {
      return false;
   }
   Minesweeper.hidden[i] = false;
   var hit = Board.hint(i);
   if (hit == Board.MINE_VAL) {
      return true;
   } else if (hit == 0) {
      Board.adjacent(i).forEach(function(j) {
         Minesweeper.reveal(j);
      });
   }
   return false;
};

Minesweeper.dump = function(markMask) {
   Board.dump(Minesweeper.hidden, markMask);
};

Player = {};

Player.init = function() {
   Minesweeper.init(100, 30, 30);
   Player.errors = 0;
   Player.marked = [];
   for (var i = 0; i < len(Board.grid); i++) {
      Player.marked.push(false);
   }
   document.querySelector(TABLE_SELECTOR).addEventListener('click', function(evt) {
      Player.reveal(parseInt(evt.srcElement.getAttribute('index')));
      Player.dump();
   });
};

Player.complete = function(self) {
   function mismatched(mark, hide, val) {
      return hide && ((val == Board.MINE_VAL) != mark);
   }
   for (var i = 0; i < Player.marked.length; i++) {
      if (mismatched(Player.marked[i], Game.hidden[i], Board.grid[i])) {
         return false;
      }
   }
   return true;
};

Player.mark = function(i, check) {
   if (check && Minesweeper.board.grid[i] != Board.MINE_VAL)
      console.log('Marked a non-mine!');
   Player.marked[i] = true;
};

Player.dump = function() {
   Minesweeper.dump(Player.marked);
};

Player.reveal = function(i) {
   return Minesweeper.reveal(i);
};

Player.state = function() {
   return Board.masked(Minesweeper.hidden, Player.marked)
};

Player.sweep = function() {
   function mines(hint, adjacent, marked, unknown) {
      return len(unknown) == hint - len(marked) ? unknown : [];
   }
   return Player.infer(mines, partial(Player.mark, check=true));
};

Player.eliminate = function() {
   function safe(hint, adjacent, marked, unknown) {
      return hint - len(marked) == 0 ? unknown : [];
   }
   return Player.infer(safe, Player.reveal);
};

// applies 'applyFn' to every index returned by selectFn when passed
// (hint, adjacent, marked, unknown) for every informative hint on the
// board. 'applyFn' is only called after all 'selectFn' calls have been
// completed. returns true if anything was applied, false otherwise.
Player.infer = function(selectFn, applyFn) {
   matching = []

   state = Player.state()
   for (var i = 0; i < len(Player.marked); i++) {
      var hint = state[i];

      // Only consider useful hints that are known.
      if (hint <= 0)
         continue;

      var adjacent = Board.adjacent(i);

      var marked = adjacent.filter(function(j) {
         return state[j] == Board.MARKED_VAL || state[j] == Board.MINE_VAL;
      });
      var unknown = adjacent.filter(function(j){
         return state[j] == Board.HIDDEN_VAL;
      });

      selectFn(hint, adjacent, marked, unknown).forEach(function(i) {
         matching.push(i);
      });
   }
   matching.forEach(applyFn(i));
   return len(matching) != 0;
};

Player.guess = function() {
   var state = Player.state()
   var unknown = xrange(0, len(Player.marked)).filter(function(i) {
      return state[i] == Board.HIDDEN_VAL;
   });
   if (len(unknown) == 0)
      return false;
   return Player.reveal(unknown[parseInt(Math.random() * unknown.length)]);
}

