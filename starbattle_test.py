from starbattle import get_cells, verify_solution

def test_get_cells():
    filename = "example_cells.txt"
    cells = get_cells(filename)
    assert cells == [[0, 0, 1, 1, 1], [0, 0, 1, 2, 2], [
        3, 3, 1, 2, 2], [3, 3, 3, 2, 4], [3, 3, 4, 4, 4]]

def test_verify_simple():
    matrix = [[0]]
    solution = [[1]]
    assert verify_solution(1, matrix, solution)

    solution2 = [[0]]
    assert not verify_solution(1, matrix, solution2)

def test_verify_5():
    matrix = [[0,0,1,1,1],
              [0,0,1,2,2],
              [3,3,1,2,2],
              [3,3,3,2,4],
              [3,3,4,4,4]]

    solution = [[0,0,0,0,1],
                [0,1,0,0,0],
                [0,0,0,1,0],
                [1,0,0,0,0],
                [0,0,1,0,0]]
    assert verify_solution(1, matrix, solution)

    solution2 = [[0,0,0,0,1],
                [0,1,0,0,0],
                [0,0,0,1,0],
                [1,0,0,0,0],
                [0,0,0,1,0]]
    assert not verify_solution(1, matrix, solution2)

    solution3 = [[0,1,0,0,1],
                [0,0,0,0,0],
                [0,0,0,1,0],
                [1,0,0,0,0],
                [0,0,1,0,0]]
    assert not verify_solution(1, matrix, solution3)

    solution4 = [[0,0,0,0,1],
                [0,0,1,0,0],
                [1,0,0,0,0],
                [0,0,0,1,0],
                [0,1,0,0,0]]
    assert not verify_solution(1, matrix, solution4)

    solution5 = [[0,0,0,0,1],
                [0,1,0,0,0],
                [1,0,0,0,0],
                [0,0,0,1,0],
                [0,0,1,0,0]]
    assert not verify_solution(1, matrix, solution5)
