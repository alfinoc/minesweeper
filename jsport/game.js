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
Board.DISPLAY[Board.MINE_VAL] = ['red', '&circledast;'];
Board.DISPLAY[Board.HIDDEN_VAL] = ['gray', '&square;'];
Board.DISPLAY[Board.MARKED_VAL] = ['pink', '&And;'];
Board.DISPLAY[0] = ['gray', ' '];

Board.init = function(mines, width, height) {
   Board.width = width;
   Board.height = height;
   var grid = [];
   for (var i = 0; i < mines; i++)
      grid.push(Board.MINE_VAL);
   for (var i = 0; i < width * height - mines; i++)
      grid.push(0);
   shuffle(grid);
   for (var i = 0; i < grid.length; i++)
      grid[i] = Board._computeHint(grid, i);
   Board.grid = grid;
}

Board.hint = function(i) {
   return Board.grid[i];
}

Board._computeHint = function(grid, index) {
   if (grid[index] == Board.MINE_VAL) {
      return Board.MINE_VAL;
   } else {
      var adjacent = 0;
      Board.adjacent(index).forEach(function(i) {
         adjacent += grid[i] == Board.MINE_VAL ? 1 : 0;
      });
      return adjacent;
   }
};

Board.format = function(index, hint) {
   hint = parseInt(hint);
   var d = Board.DISPLAY[hint];
   var color = d ? d[0] : Color.toColor(hint);
   var character = d ? d[1] : hint;
   return [color, character];
};

Board.element = function(index, hint) {
   var format = Board.format(index, hint);
   var td = document.createElement('td');
   td.setAttribute('color', format[0]);
   td.setAttribute('index', index);
   td.innerHTML = format[1];
   return td;
};

Board.dump = function(hideMask, markMask) {
   var parent = document.querySelector(TABLE_SELECTOR);
   var masked = Board.masked(hideMask, markMask);
   if (parent.innerHTML.trim().length == 0) {
      // Reload a fresh table of 'td' elements.
      parent.innerHTML = '';
      for (var i = 0; i < Board.height; i++) {
         var row = document.createElement('tr');
         for (var j = 0; j < Board.width; j++) {
            var index = j + i * Board.width;
            row.appendChild(Board.element(index, masked[index]));
         }
         parent.appendChild(row);
      }
   } else {
      // Update existing 'td' elements.
      var cells = document.querySelectorAll('td');
      for (var i = 0; i < cells.length; i++) {
         var element = cells[i];
         var index = parseInt(element.getAttribute('index'));
         var format = Board.format(index, masked[index])
         element.setAttribute('color', format[0]);
         element.innerHTML = format[1];
      }
   }
};

Board.masked = function(hideMask, markMask) {
   function apply(original, mask, replace) {
      var res = [];
      for (var i = 0; i < original.length; i++)
         res.push(mask != undefined && mask[i] ? replace : original[i]);
      return res;
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
   return pairs.map(Board.toIndex);
}

Board.toIndex = function(pair) {
   return pair[0] + pair[1] * Board.width
}

Board.toCoordinates = function(i) {
   return [i % Board.width, parseInt(i / Board.width)];
};

Minesweeper = {};

Minesweeper.init = function(mines, width, height) {
   Board.init(mines, width, height);
   Minesweeper.hidden = []
   for (var i = 0; i < Board.grid.length; i++)
      Minesweeper.hidden.push(true);
};

Minesweeper.reveal = function(i) {
   if (!Minesweeper.hidden[i])
      return false;
   Minesweeper.hidden[i] = false;
   var hit = Board.hint(i);
   if (hit == Board.MINE_VAL)
      return true;
   else if (hit == 0) {
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

Player.init = function(mines, width, height) {
   Minesweeper.init(mines, width, height);
   Player.errors = 0;
   Player.marked = [];
   for (var i = 0; i < Board.grid.length; i++)
      Player.marked.push(false);
   document.querySelector(TABLE_SELECTOR).addEventListener('click', function(evt) {
      var action = event.shiftKey ? Player.mark : Player.reveal;
      action(parseInt(evt.srcElement.getAttribute('index')));
      Player.dump();
   });
};

Player.complete = function(self) {
   function mismatched(mark, hide, val) {
      return hide && ((val == Board.MINE_VAL) != mark);
   }
   for (var i = 0; i < Player.marked.length; i++)
      if (mismatched(Player.marked[i], Minesweeper.hidden[i], Board.grid[i]))
         return false;
   return true;
};

Player.mark = function(i) {
   if (Board.grid[i] != Board.MINE_VAL)
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
      return unknown.length == hint - marked.length ? unknown : [];
   }
   var res = Player.infer(mines, Player.mark);
   Player.dump();
   return res;
};

Player.eliminate = function() {
   function safe(hint, adjacent, marked, unknown) {
      return hint - marked.length == 0 ? unknown : [];
   }
   var res = Player.infer(safe, Player.reveal);
   Player.dump();
   return res;
};

// applies 'applyFn' to every index returned by selectFn when passed
// (hint, adjacent, marked, unknown) for every informative hint on the
// board. 'applyFn' is only called after all 'selectFn' calls have been
// completed. returns true if anything was applied, false otherwise.
Player.infer = function(selectFn, applyFn) {
   var matching = [];
   var state = Player.state();

   for (var i = 0; i < Player.marked.length; i++) {
      var hint = state[i];

      // Only consider useful hints that are known.
      if (hint <= 0)
         continue;

      var adjacent = Board.adjacent(i);

      var marked = adjacent.filter(function(j) {
         return state[j] == Board.MARKED_VAL || state[j] == Board.MINE_VAL;
      });
      var unknown = adjacent.filter(function(j) {
         return state[j] == Board.HIDDEN_VAL;
      });

      selectFn(hint, adjacent, marked, unknown).forEach(function(i) {
         matching.push(i);
      });
   }
   matching.forEach(applyFn);
   return matching.length != 0;
};

Player.guess = function() {
   var state = Player.state()
   var unknown = [];
   for (var i = 0; i < Player.marked.length; i++)
      if (state[i] == Board.HIDDEN_VAL)
         unknown.push(i);
   if (unknown.length == 0)
      return false;
   return Player.reveal(unknown[parseInt(Math.random() * unknown.length)]);
};

Player.auto = function(interval) {
   while (!Player.complete()) {
      var progress = true;
      while (progress) {
         progress = false;
         progress = progress || Player.sweep();
         progress = progress || Player.eliminate();
      }
      Player.guess();
   }
   console.log('final score:' + Player.errors);
};

// Disable selection on the entire page.
function disableselect(e) { return false; }
function reEnable() { return true; }
document.onselectstart = new Function('return false');
if (window.sidebar) {
   document.onmousedown = disableselect;
   document.onclick = reEnable;
}

function shuffle(array) {
   var currentIndex = array.length, temporaryValue, randomIndex;
   while (0 !== currentIndex) {
      randomIndex = Math.floor(Math.random() * currentIndex);
      currentIndex -= 1;
      temporaryValue = array[currentIndex];
      array[currentIndex] = array[randomIndex];
      array[randomIndex] = temporaryValue;
   }
  return array;
}
