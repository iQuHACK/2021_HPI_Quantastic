from collections import defaultdict
from dimod import BinaryQuadraticModel, BINARY
from dimod.generators.constraints import combinations
from dwave.system import LeapHybridSampler

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
            return False, "one row has {} stars".format(sum(row))

    # Step 2: verify that n stars / row
    for columnID in range(width):
        total_stars = 0
        for row in solution:
            if row[columnID] == 1:
                total_stars += 1
        if total_stars != num_stars:
            return False, "one column has {} stars".format(total_stars)

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
            return False, "block {} has {} stars".format(block, stars_per_block[block])

    # Step 4: verify that no stars are adjacent
    for y in range(width):
        for x in range(width):
            if solution[y][x] and has_neighboring_star(solution, y, x):
                return False, "stars are adjacent at y={}, x={}".format(y,x)

    return True, ""

def build_bqm(cells, num_stars):
    bqm = BinaryQuadraticModel({}, {}, 0.0, BINARY)

    # constraint 1: n stars per row
    for y, row in enumerate(cells):
        row_coords = [(y,x) for x,_ in enumerate(row)]
        row_bqm = combinations(row_coords, num_stars)
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


def full_solution(cells, num_stars):
    bqm = build_bqm(cells, num_stars)
    sampleset = LeapHybridSampler().sample(bqm, time_limit=5)
    return sample_to_solution(sampleset.first.sample, len(cells))

