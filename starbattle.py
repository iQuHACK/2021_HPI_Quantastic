import sys
from collections import defaultdict
import dimod
from dimod.generators.constraints import combinations
from hybrid.reference import KerberosSampler
from colorama import init, Fore

def parse_file(filename):
    """Return a list of lists containing the content of the input text file.

    Note: each line of the text file corresponds to a list. Each item in
    the list is from splitting the line of text by the whitespace ' '.
    """
    with open(filename, "r") as f:
        content = f.read().rstrip().split('\n')

    num_stars = int(content[0])
    if num_stars <= 0:
        raise ValueError("invalid number of stars")

    cells = [ list(map(int, line.split(' '))) for line in content[1:] ]

    if len(set(map(len, cells))) != 1:
        raise ValueError("rows must have the same length")
    if len(cells[0]) != len(cells):
        raise ValueError("board must me quadratic")

    return cells, num_stars

def neighbors(y, x, width):
    start_y = 0 if y == 0 else y-1
    end_y = width-1 if y == width-1 else y+1

    start_x = 0 if x == 0 else x-1
    end_x = width-1 if x == width-1 else x+1

    neighbors = set()
    for i in range(start_y, end_y+1):
        for k in range(start_x, end_x+1):
            if i != y or k != x:
                neighbors.add((i,k))
    return neighbors

def has_neighboring_star(solution, y, x):
    for neighbor in neighbors(y, x, len(solution)):
        if solution[neighbor[0]][neighbor[1]] == 1 and (neighbor[0] != y or neighbor[1] != x):
            return True
    return False

def verify_solution(num_stars, cells, solution):
    width = len(cells)

    # Step 1: verify that n stars / row
    for row in solution:
        if sum(row) != num_stars:
            return False

    # Step 2: verify that n stars / row
    for columnID in range(width):
        total_stars = 0
        for row in solution:
            if row[columnID] == 1:
                total_stars += 1
        if total_stars != num_stars:
            return False

    # Step 3: verify that n stars / block
    stars_per_block = {}
    for y, row in enumerate(cells):
        for x, cell in enumerate(row):
            if cell not in stars_per_block:
                stars_per_block[cell] = 0
            if solution[y][x] == 1:
                stars_per_block[cell] += 1

    for block in stars_per_block:
        if stars_per_block[block] != num_stars:
            return False

    # Step 4: verify that no stars are adjacent
    for y in range(width):
        for x in range(width):
            if solution[y][x] and has_neighboring_star(solution, y, x):
                return False

    return True

def build_bqm(cells, num_stars):
    bqm = dimod.BinaryQuadraticModel({}, {}, 0.0, dimod.BINARY)

    # constraint 1: n stars per row
    for y, row in enumerate(cells):
        row_labels = [(y,x) for x,_ in enumerate(row)]
        row_bqm = combinations(row_labels, num_stars)
        bqm.update(row_bqm)

    # constraint 2: n stars per column
    for x in range(len(cells[0])):
        col_labels = [(y,x) for y in range(len(cells))]
        col_bqm = combinations(col_labels, num_stars)
        bqm.update(col_bqm)

    # constraint 3: n stars per block
    block_to_labels = defaultdict(list)
    for y, row in enumerate(cells):
        for x, cell in enumerate(row):
            block_to_labels[cell].append((y,x))

    for block in block_to_labels:
        block_bqm = combinations(block_to_labels[block], num_stars)
        bqm.update(block_bqm)

    # constraint 4: no adjacent stars
    for y, row in enumerate(cells):
        for x, _ in enumerate(row):
            for neighbor in neighbors(y, x, len(cells)):
                bqm.add_interaction((y,x), (neighbor[0],neighbor[1]), 1)
    return bqm

def sample_to_solution(sample, width):
    solution = [[ 0 for _ in range(width) ] for _ in range(width)]
    for coords in sample:
        solution[coords[0]][coords[1]] = sample[coords]
    return solution

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

if __name__ == "__main__":

    # Read user input
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "example_cells.txt"
        print("Warning: using default problem file, '{}'. Usage: python "
              "{} <cells filepath>".format(filename, sys.argv[0]))


    cells, num_stars = parse_file(filename)

    init()
    print("problem:")
    print_cells(cells)
    print()

    bqm = build_bqm(cells, num_stars)
    sampleset = KerberosSampler().sample(bqm, max_iter=10, qpu_params={'label': 'Starbattle'})
    solution = sample_to_solution(sampleset.first.sample, len(cells))

    if verify_solution(num_stars, cells, solution):
        print("found valid solution:")
    else:
        print("found invalid solution:")
    print_solution(solution)
