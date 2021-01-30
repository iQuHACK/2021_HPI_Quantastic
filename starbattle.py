import dimod
from dimod.generators.constraints import combinations
from collections import defaultdict
from hybrid.reference import KerberosSampler
import sys


def get_cells(filename):
    """Return a list of lists containing the content of the input text file.

    Note: each line of the text file corresponds to a list. Each item in
    the list is from splitting the line of text by the whitespace ' '.
    """
    with open(filename, "r") as f:
        content = f.read().split('\n')

    lines = []
    length = len(content[0])
    for line in content:
        new_line = line.rstrip()    # Strip any whitespace after last value
        if (len(line) != length):   # Ensures that all rows have the same length
            raise ValueError("Check that all rows have the same length")
        if new_line:
            new_line = list(map(int, new_line.split(' ')))
            lines.append(new_line)

    return lines

def neighbors(y, x, height, width):
    start_y = 0 if y == 0 else y-1
    end_y = height-1 if y == height-1 else y+1

    start_x = 0 if x == 0 else x-1
    end_x = width-1 if x == width-1 else x+1

    neighbors = set()
    for i in range(start_y, end_y+1):
        for k in range(start_x, end_x+1):
            if i != y or k != x:
                neighbors.add((i,k))
    return neighbors

def has_neighboring_star(solution, y, x):
    for neighbor in neighbors(y, x, len(solution), len(solution[0])):
        if solution[neighbor[0]][neighbor[1]] == 1 and (neighbor[0] != y or neighbor[1] != x):
            return True
    return False

def verify_solution(n, cells, solution):
    height = len(cells)
    width = len(cells[0])

    # Step 1: verify that n stars / row
    for row in solution:
        if sum(row) != n:
            return False

    # Step 2: verify that n stars / row
    for columnID in range(width):
        total_stars = 0
        for row in solution:
            if row[columnID] == 1:
                total_stars += 1
        if total_stars != n:
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
        if stars_per_block[block] != n:
            return False

    # Step 4: verify that no stars are adjacent
    for y in range(height):
        for x in range(width):
            if solution[y][x] and has_neighboring_star(solution, y, x):
                return False

    return True

def get_label(y, x):
    return '{},{}'.format(y,x)

def build_bqm(cells, n):
    bqm = dimod.BinaryQuadraticModel({}, {}, 0.0, dimod.BINARY)

    # constraint 1: n stars per row
    for y, row in enumerate(cells):
        row_labels = [get_label(y,x) for x,_ in enumerate(row)]
        row_bqm = combinations(row_labels, n)
        bqm.update(row_bqm)

    # constraint 2: n stars per column
    for x in range(len(cells[0])):
        col_labels = [get_label(y, x) for y in range(len(cells))]
        col_bqm = combinations(col_labels, n)
        bqm.update(col_bqm)

    # constraint 3: n stars per block
    block_to_labels = defaultdict(list)
    for y, row in enumerate(cells):
        for x, cell in enumerate(row):
            block_to_labels[cell].append(get_label(y, x))

    for block in block_to_labels:
        block_bqm = combinations(block_to_labels[block], n)
        bqm.update(block_bqm)

    # constraint 4: no adjacent stars
    for y, row in enumerate(cells):
        for x, _ in enumerate(row):
            for neighbor in neighbors(y, x, len(cells), len(cells[0])):
                bqm.add_interaction(get_label(y,x), get_label(neighbor[0], neighbor[1]), 1)
    return bqm


if __name__ == "__main__":
    # Read user input
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "example_cells.txt"
        print("Warning: using default problem file, '{}'. Usage: python "
              "{} <cells filepath>".format(filename, sys.argv[0]))

    cells = get_cells(filename)
    bqm = build_bqm(cells, 1)

    solution = KerberosSampler().sample(bqm, max_iter=10, qpu_params={'label': 'Starbattle'})
    print(solution.first.sample)
