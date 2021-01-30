import dimod
from dimod.generators.constraints import combinations
import sys

def get_cells(filename):
    """Return a list of lists containing the content of the input text file.

    Note: each line of the text file corresponds to a list. Each item in
    the list is from splitting the line of text by the whitespace ' '.
    """
    with open(filename, "r") as f:
        content = f.readlines()

    lines = []
    for line in content:
        new_line = line.rstrip()    # Strip any whitespace after last value

        if new_line:
            new_line = list(map(int, new_line.split(' ')))
            lines.append(new_line)

    return lines

def has_neighboring_star(solution, y, x):
    start_y = 0 if y == 0 else y-1
    end_y = len(solution)-1 if y == len(solution)-1 else y+1

    start_x = 0 if x == 0 else x-1
    end_x = len(solution[0])-1 if x == len(solution[0])-1 else x+1

    for i in range(start_y, end_y+1):
        for k in range(start_x, end_x+1):
            if solution[i][k] == 1 and (i != y or k != x):
                return True
    return False

def verify_solution(n, matrix, solution):
    height = len(matrix)
    width = len(matrix[0])

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
    for y, row in enumerate(matrix):
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


if __name__ == "__main__":
    # Read user input
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "example_cells.txt"
        print("Warning: using default problem file, '{}'. Usage: python "
              "{} <cells filepath>".format(filename, sys.argv[0]))

    cells = get_cells(filename)
