import othello_base_GUI as ob
import random

SQUARE_WEIGHTS = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 120, -20, 20, 5, 5, 20, -20, 120, 0,
    0, -20, -40, -5, -5, -5, -5, -40, -20, 0,
    0, 20, -5, 15, 3, 3, 15, -5, 20, 0,
    0, 5, -5, 3, 3, 3, 3, -5, 5, 0,
    0, 5, -5, 3, 3, 3, 3, -5, 5, 0,
    0, 20, -5, 15, 3, 3, 15, -5, 20, 0,
    0, -20, -40, -5, -5, -5, -5, -40, -20, 0,
    0, 120, -20, 20, 5, 5, 20, -20, 120, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
]

# Values for endgame boards are big constants.
MAX_VALUE = sum(map(abs, SQUARE_WEIGHTS))
MIN_VALUE = -MAX_VALUE


class v0001(ob.OthelloGUI):
    # The easiest strategy to implement simply picks a move at random.    
    def random_strategy(self, player, board):
        """A strategy that always chooses a random legal move."""
        return random.choice(self.legal_moves(player, board))
    
    
    # <a id="localmax"></a>
    ### Local maximization
    
    # A more sophisticated strategy could look at every available move and evaluate
    # them in some way.  This consists of getting a list of legal moves, applying
    # each one to a copy of the board, and choosing the move that results in the
    # "best" board.
    
    def maximizer(self, evaluate):
        """
        Construct a strategy that chooses the best move by maximizing
        evaluate(player, board) over all boards resulting from legal moves.
        """
    
        def strategy(player, board):
            def score_move(move):
                return evaluate(player, self.make_move(move, player, list(board)))
    
            return max(self.legal_moves(player, board), key=score_move)
    
        return strategy
    
    
    # One possible evaluation function is `score`.  A strategy constructed with
    # `maximizer(score)` will always make the move that results in the largest
    # immediate gain in pieces.
    
    # A more advanced evaluation function might consider the relative worth of each
    # square on the board and weight the score by the value of the pieces held by
    # each player.  Since corners and (most) edge self.squares are very valuable, we
    # could weight those more heavily, and add negative weights to the self.squares that,
    # if acquired, could lead to the self.opponent capturing the corners or edges.
    
    
    
    # A strategy constructed as `maximizer(weighted_score)`, then, will always
    # return the move that results in the largest immediate *weighted* gain in
    # pieces.
    
    def weighted_score(self, player, board):
        """
        Compute the difference between the sum of the weights of player's
        self.squares and the sum of the weights of self.opponent's self.squares.
        """
        opp = self.opponent(player)
        total = 0
        for sq in self.squares():
            if board[sq] == player:
                total += SQUARE_WEIGHTS[sq]
            elif board[sq] == opp:
                total -= SQUARE_WEIGHTS[sq]
        return total
    
    
    # <a id="self.minimax"></a>
    ### self.minimax search
    
    # The maximizer strategies are very short-sighted, and a player who can consider
    # the implications of a move several turns in advance could have a significant
    # advantage.  The **self.minimax** algorithm does just that.
    
    def minimax(self, player, board, depth, evaluate):
        """
        Find the best legal move for player, searching to the specified depth.
        Returns a tuple (move, min_score), where min_score is the guaranteed minimum
        score achievable for player if the move is made.
        """
    
        # We define the value of a board to be the opposite of its value to our
        # self.opponent, computed by recursively applying `self.minimax` for our self.opponent.
        def value(board):
            return -self.minimax(self.opponent(player), board, depth - 1, evaluate)[0]
    
        # When depth is zero, don't examine possible moves--just determine the value
        # of this board to the player.
        if depth == 0:
            return evaluate(player, board), None
    
        # We want to evaluate all the legal moves by considering their implications
        # `depth` turns in advance.  First, find all the legal moves.
        moves = self.legal_moves(player, board)
    
        # If player has no legal moves, then either:
        if not moves:
            # the game is over, so the best achievable score is victory or defeat;
            if not self.any_legal_move(self.opponent(player), board):
                return self.final_value(player, board), None
            # or we have to pass this turn, so just find the value of this board.
            return value(board), None
    
        # When there are multiple legal moves available, choose the best one by
        # maximizing the value of the resulting boards.
        return max((value(self.make_move(m, player, list(board))), m) for m in moves)
    

    
    def final_value(self, player, board):
        """The game is over--find the value of this board to player."""
        diff = self.score(player, board)
        if diff < 0:
            return MIN_VALUE
        elif diff > 0:
            return MAX_VALUE
        return diff
    
    
    def minimax_searcher(self, depth, evaluate):
        """
        Construct a strategy that uses `self.minimax` with the specified leaf board
        evaluation function.
        """
    
        def strategy(player, board):
            return self.minimax(player, board, depth, evaluate)[1]
    
        return strategy
    
    
    # <a id="alphabeta"></a>
    ### Alpha-Beta search
    
    # self.minimax is very effective, but it does too much work: it evaluates many search
    # trees that should be ignored.
    
    # Consider what happens when self.minimax is evaluating two moves, M1 and M2, on one
    # level of a search tree.  Suppose self.minimax determines that M1 can result in a
    # score of S.  While evaluating M2, if self.minimax finds a move in its subtree that
    # could result in a better score than S, the algorithm should immediately quit
    # evaluating M2: the self.opponent will force us to play M1 to avoid the higher score
    # resulting from M1, so we shouldn't waste time determining just how much better
    # M2 is than M1.
    
    # We need to keep track of two values:
    #
    # - alpha: the maximum score achievable by any of the moves we have encountered.
    # - beta: the score that the self.opponent can keep us under by playing other moves.
    #
    # When the algorithm begins, alpha is the smallest value and beta is the largest
    # value.  During evaluation, if we find a move that causes `alpha >= beta`, then
    # we can quit searching this subtree since the self.opponent can prevent us from
    # playing it.
    
    def alphabeta(self, player, board, alpha, beta, depth, evaluate):
        """
        Find the best legal move for player, searching to the specified depth.  Like
        self.minimax, but uses the bounds alpha and beta to prune branches.
        """
        if depth == 0:
            return evaluate(player, board), None
    
        def value(board, alpha, beta):
            # Like in `self.minimax`, the value of a board is the opposite of its value
            # to the self.opponent.  We pass in `-beta` and `-alpha` as the alpha and
            # beta values, respectively, for the self.opponent, since `alpha` represents
            # the best score we know we can achieve and is therefore the worst score
            # achievable by the self.opponent.  Similarly, `beta` is the worst score that
            # our self.opponent can hold us to, so it is the best score that they can
            # achieve.
            return -self.alphabeta(self.opponent(player), board, -beta, -alpha, depth - 1, evaluate)[0]
    
        moves = self.legal_moves(player, board)
        if not moves:
            if not self.any_legal_move(self.opponent(player), board):
                return self.final_value(player, board), None
            return value(board, alpha, beta), None
    
        best_move = moves[0]
        for move in moves:
            if alpha >= beta:
                # If one of the legal moves leads to a better score than beta, then
                # the self.opponent will avoid this branch, so we can quit looking.
                break
            val = value(self.make_move(move, player, list(board)), alpha, beta)
            if val > alpha:
                # If one of the moves leads to a better score than the current best
                # achievable score, then replace it with this one.
                alpha = val
                best_move = move
        return alpha, best_move
    
    
    def alphabeta_searcher(self, depth, evaluate):
        def strategy(player, board):
            return self.alphabeta(player, board, MIN_VALUE, MAX_VALUE, depth, evaluate)[1]
    
        return strategy
    
    
        # -----------------------------------------------------------------------------
        # <a id="conclusion"></a>
        ## Conclusion
    
        # The strategies we've discussed are very general and are applicable to a broad
        # range of strategy games, such as Chess, Checkers, and Go.  More advanced
        # strategies for Othello exist that apply various gameplay heuristics; some of
        # these are discussed in "Paradigms of Artificial Intelligence Programming" by
        # Peter Norvig.
        #
        # See Wikipedia for more details on [self.minimax][mm] and [alpha-beta][ab] search.
        #
        # [mm]: http://en.wikipedia.org/wiki/self.minimax
        # [ab]: http://en.wikipedia.org/wiki/Alpha-beta_pruning
