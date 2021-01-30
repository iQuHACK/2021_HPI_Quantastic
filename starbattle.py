import dimod
from dimod.generators.constraints import combinations
import sys


def verify_solution(matrix, solution):
    pass


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


if __name__ == "__main__":
    # Read user input
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "example_cells.txt"
        print("Warning: using default problem file, '{}'. Usage: python "
              "{} <cells filepath>".format(filename, sys.argv[0]))

    cells = get_cells(filename)
