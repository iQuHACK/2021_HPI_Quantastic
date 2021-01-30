from starbattle import get_cells


def test_get_cells():
    filename = "example_cells.txt"
    cells = get_cells(filename)
    assert cells == [[0, 0, 1, 1, 1], [0, 0, 1, 2, 2], [
        3, 3, 1, 2, 2], [3, 3, 3, 2, 4], [3, 3, 4, 4, 4]]


def test_test():
    assert 3 == 3
