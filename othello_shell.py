import othello_v0001 as ob
from multiprocessing import Process, Value, Array

othello=ob.v0001()

def human(player, board):
    print(othello.print_board(board))
    print('Your move?')
    while True:
        move = input('> ')
        if move and check(int(move), player, board):
            return int(move)
        elif move:
            print('Illegal move--try again.')

options = {'human': human,
           'random': othello.random_strategy,
           'max-diff': othello.maximizer(othello.score),
           'max-weighted-diff': othello.maximizer(othello.weighted_score),
           'minimax-diff': othello.minimax_searcher(3, othello.score),
           'minimax-weighted-diff':
               othello.minimax_searcher(3, othello.weighted_score),
           'ab-diff': othello.alphabeta_searcher(3, othello.score),
           'ab-weighted-diff':
               othello.alphabeta_searcher(3, othello.weighted_score)}

def check(move, player, board):
    return othello.is_valid(move) and othello.is_legal(move, player, board)



def get_choice(prompt, options):
    print(prompt)
    print('Options:', list(options.keys()))
    while True:
        choice = input('> ')
        if choice in options:
            return options[choice]
        elif choice:
            print('Invalid choice.')

def get_players():
    print('Welcome to OTHELLO!')
    black = get_choice('BLACK: choose a strategy', options)
    white = get_choice('WHITE: choose a strategy', options)
    return black, white

def main(black_choice = None, white_choice = None, black_name="Black", white_name="White"):
    try:
        if (black_choice == None or white_choice == None):
            #black, white = get_players()
            black, white = othello.alphabeta_searcher(6, othello.weighted_score), \
                           othello.alphabeta_searcher(6, othello.weighted_score)
            black_name, white_name = "Alpha-Beta 8a", "Alpha-Beta 8b"
            #black, white = othello.random_strategy, othello.maximizer(othello.score)
        else:
            (black, white) = [options[k] for k in (black_choice, white_choice)]
        board, score1 = othello.play(black, white, black_name, white_name)
        #board, score2 = othello.play(black, white, black_name, white_name)
        #board, score3 = othello.play(black, white, black_name, white_name)
        othello.end_wait()

    except othello.IllegalMoveError as e:
        print(e)
        return
    except EOFError as e:
        print('Goodbye!')
        return
    print('Final score:', score1)
    print('%s wins!' % ('Black' if score1 > 0 else 'White'))
    print(othello.print_board(board))

if __name__=="__main__":
    main()