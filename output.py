from colorama import init as colorama_init, Fore
from starbattle import full_solution, verify_solution

def init():
    colorama_init()

def print_solution(solution):
    for row in solution:
        for cell in row:
            if cell == 1:
                print(Fore.YELLOW + "*" + Fore.RESET, end=" ")
            else:
                print("- ", end="")
        print(Fore.RESET)

def print_cells(cells):
    SYMBOLS = {
        0: ('/', Fore.RED),
        1: ('$', Fore.GREEN),
        2: ('?', Fore.YELLOW),
        3: ('|', Fore.BLUE),
        4: ('%', Fore.MAGENTA),
        5: ('(', Fore.CYAN),
        6: ('§', Fore.WHITE),
        7: ('+', Fore.LIGHTRED_EX),
        8: ('_', Fore.LIGHTGREEN_EX),
        9: ('&', Fore.LIGHTYELLOW_EX),
        10: ('~', Fore.LIGHTBLUE_EX),
        11: ('#', Fore.LIGHTMAGENTA_EX),
        12: ('^', Fore.LIGHTCYAN_EX),
        13: ('=', Fore.LIGHTWHITE_EX),
    }
    for y,row in enumerate(cells):
        for x,cell in enumerate(row):
            print(SYMBOLS[cell][1] + SYMBOLS[cell][0] if cell < len(SYMBOLS) else cell, end=" ")
        print(Fore.RESET)

def solve_with_output(cells, num_stars):
    init()
    print("problem:")
    print_cells(cells)
    print()

    solution = full_solution(cells, num_stars)
    print("checking solution...")
    if verify_solution(num_stars, cells, solution):
        print("found valid solution:")
    else:
        print("found invalid solution:")
    print_solution(solution)
