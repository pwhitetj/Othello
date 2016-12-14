from tkinter import *
import time

# othello=ob.v0001()

root = Tk()
p1_strategy_int = IntVar()
p2_strategy_int = IntVar()

options = [("Random", 'random'),
           ("Max-Diff", 'max-diff'),
           ("Max Weighted Diff", 'max-weighted-diff'),
           ("Minimax Diff (3)", 'minimax-diff'),
           ("Minimax Weighted Diff (3)", 'minimax-weighted-diff'),
           ("Alpha-Beta Diff (3)", 'ab-diff'),
           ("Alpha-Beta Weighted Diff (3)", 'ab-weighted-diff')]

lframe_1 = LabelFrame(root, text="Player 1 Strategy")
lframe_2 = LabelFrame(root, text="Player 2 Strategy")


player1_choices = []
for (idx, key) in enumerate(options):
    player1_choices.append(Radiobutton(lframe_1, text=key[0],
                                       variable=p1_strategy_int,
                                       value=idx))
player2_choices = []
for (idx, key) in enumerate(options):
    player2_choices.append(Radiobutton(lframe_2, text=key[0],
                                       variable=p2_strategy_int,
                                       value=idx))


for button in player1_choices:
    button.pack(anchor=N)
for button in player2_choices:
    button.pack(anchor=N)
lframe_1.pack(fill = "both", expand = "yes", anchor = W)
lframe_2.pack(fill = "both", expand = "yes", anchor = E)

def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))


menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Exit", command=root.destroy)
menubar.add_cascade(label="File", menu=filemenu)
root.config(menu=menubar)

center(root)

root.lift()
root.focus_set()
root.mainloop()
root.quit()

print("still looping")
black = options[p1_strategy_int.get()]
white = options[p2_strategy_int.get()]
print(black[0], 'vs', white[0])

import othello_shell as shell
shell.main(black[1], white[1], black[0], white[0])