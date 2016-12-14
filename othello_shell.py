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

def main(black_choice, white_choice, black_name="Black", white_name="White"):
    try:
        (black, white) = black_choice, white_choice
        #(black, white) = [options[k] for k in (black_choice, white_choice)]
        board, score = othello.play(black, white, black_name, white_name)
        return (board, score)
    except othello.IllegalMoveError as e:
        print(e)
        return
    except EOFError as e:
        print('Goodbye!')
        return
    print('Final score:', score )
    print('%s wins!' % ('Black' if score  > 0 else 'White'))
    print(othello.print_board(board))

if __name__=="__main__":
    strategy_A = othello.time_limited(othello.alphabeta_searcher(5, othello.weighted_score),2)
    strategy_B = othello.time_limited(othello.alphabeta_searcher(3, othello.weighted_score),5)
    name_A = "Alpha-Beta 5"
    name_B = "Alpha-Beta 3"

    scores = []
    wins = {name_A:0, name_B:0}
    for i in range(4):
        board, score  = main(strategy_A, strategy_B, name_A, name_B)
        scores += [score]
        if score > 0:
            wins[name_A]+=1
        elif score < 0:
            wins[name_B]+=1
        (strategy_A, strategy_B) = strategy_B, strategy_A
        name_A, name_B = name_B, name_A
    print(scores, wins)
    othello.end_wait()