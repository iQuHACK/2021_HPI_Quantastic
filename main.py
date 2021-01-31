import argparse


def parse_file(filename):
    with open(filename, "r") as f:
        content = f.read().rstrip().split('\n')

    num_stars = int(content[0])
    if num_stars <= 0:
        raise ValueError("invalid number of stars")

    cells = [list(map(int, line.split(' '))) for line in content[1:]]

    if len(set(map(len, cells))) != 1:
        raise ValueError("rows must have the same length")
    if len(cells[0]) != len(cells):
        raise ValueError("board must me quadratic")

    return cells, num_stars


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="solve and play Starbattle / Two Not Touch on D-Wave Leap")
    parser.add_argument("action", choices=[
                        "solve", "play"], help="whether to solve or play the game")
    parser.add_argument("file", help="game file to load")
    args = parser.parse_args()

    cells, num_stars = parse_file(args.file)

    if args.action == "solve":
        from output import solve_with_output
        solve_with_output(cells, num_stars)
    elif args.action == "play":
        from gui import loop
        loop(cells, num_stars)
