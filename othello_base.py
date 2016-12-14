"""
**Othello** is a turn-based two-player strategy board game.  The players take
turns placing pieces--one player white and the other player black--on an 8x8
board in such a way that captures some of the opponent's pieces, with the goal
of finishing the game with more pieces of their color on the board.
Every move must capture one more more of the opponent's pieces.  To capture,
player A places a piece adjacent to one of player B's pieces so that there is a
straight line (horizontal, vertical, or diagonal) of adjacent pieces that begins
with one of player A's pieces, continues with one more more of player B's
pieces, and ends with one of player A's pieces.
For example, if Black places a piece on square (5, 1), he will capture all of
Black's pieces between (5, 1) and (5, 6):
      1 2 3 4 5 6 7 8      1 2 3 4 5 6 7 8
    1 . . . . . . . .    1 . . . . . . . .
    2 . . . . . . . .    2 . . . . . . . .
    3 . . o @ . o . .    3 . . o @ . o . .
    4 . . o o @ @ . .    4 . . o o @ @ . .
    5 . o o o o @ . .    5 @ @ @ @ @ @ . .
    6 . . . @ o . . .    6 . . . @ o . . .
    7 . . . . . . . .    7 . . . . . . . .
    8 . . . . . . . .    8 . . . . . . . .
For more more information about the game (which is also known as Reversi)
including detailed rules, see the entry on [Wikipedia][wiki].  Additionally,
this implementation doesn't take into account some tournament-style Othello
details, such as game time limits and a different indexing scheme.
We will implement representations for the board and pieces and the mechanics of
playing a game.  We will then explore several game-playing strategies.  There is
a simple command-line program [provided](examples/othello/othello.html) for
playing against the computer or comparing two strategies.
Written by [Daniel Connelly](http://dhconnelly.com).  This implementation follows
chapter 18 of Peter Norvig's "Paradigms of Artificial Intelligence".
[wiki]: http://en.wikipedia.org/wiki/Reversi
"""

# -----------------------------------------------------------------------------
## Table of contents

# 1. [Board representation](#board)
# 2. [Playing the game](#playing)
# 3. [Strategies](#strategies)
#     - [Random](#random)<br>
#     - [Local maximization](#localmax)<br>
#     - [Minimax search](#minimax)<br>
#     - [Alpha-beta search](#alphabeta)<br>
# 4. [Conclusion](#conclusion)


# -----------------------------------------------------------------------------
# <a id="board"></a>
## Board representation

# We represent the board as a 100-element list, which includes each square on
# the board as well as the outside edge.  Each consecutive sublist of ten
# elements represents a single row, and each list element stores a piece.  An
# initial board contains four pieces in the center:

#     ? ? ? ? ? ? ? ? ? ?
#     ? . . . . . . . . ?
#     ? . . . . . . . . ?
#     ? . . . . . . . . ?
#     ? . . . o @ . . . ?
#     ? . . . @ o . . . ?
#     ? . . . . . . . . ?
#     ? . . . . . . . . ?
#     ? . . . . . . . . ?
#     ? ? ? ? ? ? ? ? ? ?

# This representation has two useful properties:
#
# 1. Square (m,n) can be accessed as `board[mn]`.  This avoids the need to write
#    functions that convert between square locations and list indexes.
# 2. Operations involving bounds checking are slightly simpler.

# The outside edge is marked ?, empty squares are ., black is @, and white is o.
# The black and white pieces represent the two players.

from multiprocessing import Value

EMPTY, BLACK, WHITE, OUTER = '.', '@', 'o', '?'
PIECES = (EMPTY, BLACK, WHITE, OUTER)
PLAYERS = {BLACK: 'Black', WHITE: 'White'}

# To refer to neighbor squares we can add a direction to a square.
UP, DOWN, LEFT, RIGHT = -10, 10, -1, 1
UP_RIGHT, DOWN_RIGHT, DOWN_LEFT, UP_LEFT = -9, 11, 9, -11
DIRECTIONS = (UP, UP_RIGHT, RIGHT, DOWN_RIGHT, DOWN, DOWN_LEFT, LEFT, UP_LEFT)

class OthelloBase:
    def squares(self):
        """List all the valid squares on the board."""
        return [i for i in range(11, 89) if 1 <= (i % 10) <= 8]


    def initial_board(self):
        """Create a new board with the initial black and white positions filled."""
        board = [OUTER] * 100
        for i in self.squares():
            board[i] = EMPTY
        # The middle four squares should hold the initial piece positions.
        board[44], board[45] = WHITE, BLACK
        board[54], board[55] = BLACK, WHITE
        return board


    def print_board(self,board):
        """Get a string representation of the board."""
        rep = ''
        rep += '  %s\n' % ' '.join(map(str, list(range(1, 9))))
        for row in range(1, 9):
            begin, end = 10 * row + 1, 10 * row + 9
            rep += '%d %s\n' % (row, ' '.join(board[begin:end]))
        return rep


    # -----------------------------------------------------------------------------
    # <a id="playing"></a>
    ## Playing the game

    # We need functions to get moves from players, check to make sure that the moves
    # are legal, apply the moves to the board, and detect when the game is over.

    ### Checking moves

    # A move must be both valid and legal: it must refer to a real square, and it
    # must form a bracket with another piece of the same color with pieces of the
    # opposite color in between.

    def is_valid(self, move):
        """Is move a square on the board?"""
        return isinstance(move, int) and move in self.squares()


    def opponent(self, player):
        """Get player's opponent piece."""
        return BLACK if player is WHITE else WHITE


    def find_bracket(self, square, player, board, direction):
        """
        Find a square that forms a bracket with `square` for `player` in the given
        `direction`.  Returns None if no such square exists.
        """
        bracket = square + direction
        if board[bracket] == player:
            return None
        opp = self.opponent(player)
        while board[bracket] == opp:
            bracket += direction
        return None if board[bracket] in (OUTER, EMPTY) else bracket


    def is_legal(self, move, player, board):
        """Is this a legal move for the player?"""
        hasbracket = lambda direction: self.find_bracket(move, player, board, direction)
        return board[move] == EMPTY and any(map(hasbracket, DIRECTIONS))


    ### Making moves

    # When the player makes a move, we need to update the board and flip all the
    # bracketed pieces.

    def make_move(self, move, player, board):
        """Update the board to reflect the move by the specified player."""
        board[move] = player
        for d in DIRECTIONS:
            self.make_flips(move, player, board, d)
        return board


    def make_flips(self, move, player, board, direction):
        """Flip pieces in the given direction as a result of the move by player."""
        bracket = self.find_bracket(move, player, board, direction)
        if not bracket:
            return
        square = move + direction
        while square != bracket:
            board[square] = player
            square += direction


    ### Monitoring players

    class IllegalMoveError(Exception):
        def __init__(self, player, move, board):
            self.player = player
            self.move = move
            self.board = board

        def __str__(self):
            return '%s cannot move to square %d' % (PLAYERS[self.player], self.move)


    def legal_moves(self, player, board):
        """Get a list of all legal moves for player."""
        return [sq for sq in self.squares() if self.is_legal(sq, player, board)]


    def any_legal_move(self, player, board):
        """Can player make any moves?"""
        return any(self.is_legal(sq, player, board) for sq in self.squares())


    ### Putting it all together

    # Each round consists of:
    #
    # - Get a move from the current player.
    # - Apply it to the board.
    # - Switch players.  If the game is over, get the final score.

    def play(self,black_strategy, white_strategy):
        """Play a game of Othello and return the final board and score."""
        board = self.initial_board()
        player = BLACK
        strategy = lambda who: black_strategy if who == BLACK else white_strategy
        while player is not None:
            move = self.get_move(strategy(player), player, board)
            self.make_move(move, player, board)
            #print(self.print_board(board))
            player = self.next_player(board, player)
        return board, self.score(BLACK, board)


    def next_player(self,board, prev_player):
        """Which player should move next?  Returns None if no legal moves exist."""
        opp = self.opponent(prev_player)
        if self.any_legal_move(opp, board):
            return opp
        elif self.any_legal_move(prev_player, board):
            return prev_player
        return None


    def get_move(self, strategy, player, board, best = None, running = None):
        """Call strategy(player, board) to get a move."""
        copy = list(board)  # copy the board to prevent cheating
        move = strategy(player, copy, best, running)
        if not self.is_valid(move) or not self.is_legal(move, player, board):
            raise self.IllegalMoveError(player, move, copy)
        return move


    def score(self,player, board):
        """Compute player's score (number of player's pieces minus opponent's)."""
        mine, theirs = 0, 0
        opp = self.opponent(player)
        for sq in self.squares():
            piece = board[sq]
            if piece == player:
                mine += 1
            elif piece == opp:
                theirs += 1
        return mine - theirs

