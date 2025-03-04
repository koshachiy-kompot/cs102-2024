import pathlib
import random
import typing as tp
import multiprocessing
import threading
import time

T = tp.TypeVar("T")


def read_sudoku(path: tp.Union[str, pathlib.Path]) -> tp.List[tp.List[str]]:
    """Прочитать Судоку из указанного файла"""
    path = pathlib.Path(path)
    with path.open("r", encoding="utf-8") as f:
        puzzle = f.read()
    return create_grid(puzzle)


def create_grid(puzzle: str) -> tp.List[tp.List[str]]:
    digits = [c for c in puzzle if c in "123456789."]
    grid = group(digits, 9)
    return grid


def display(grid: tp.List[tp.List[str]]) -> None:
    """Вывод Судоку"""
    width = 2
    line = "+".join(["-" * (width * 3)] * 3)
    for row in range(9):
        print("".join(grid[row][col].center(width) + ("|" if str(col) in "25" else "") for col in range(9)))
        if str(row) in "25":
            print(line)
    print()


def group(values: tp.List[T], n: int) -> tp.List[tp.List[T]]:
    """
    Сгруппировать значения values в список, состоящий из списков по n элементов
    >>> group([1,2,3,4], 2)
    [[1, 2], [3, 4]]
    >>> group([1,2,3,4,5,6,7,8,9], 3)
    [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    """
    matrix = [values[i * len(values) // n : (i + 1) * len(values) // n] for i in range(n)]
    return matrix


def get_row(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.List[str]:
    """Возвращает все значения для номера строки, указанной в pos
    >>> get_row([['1', '2', '.'], ['4', '5', '6'], ['7', '8', '9']], (0, 0))
    ['1', '2', '.']
    >>> get_row([['1', '2', '3'], ['4', '.', '6'], ['7', '8', '9']], (1, 0))
    ['4', '.', '6']
    >>> get_row([['1', '2', '3'], ['4', '5', '6'], ['.', '8', '9']], (2, 0))
    ['.', '8', '9']
    """
    return grid[pos[0]]


def get_col(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.List[str]:
    """Возвращает все значения для номера столбца, указанного в pos
    >>> get_col([['1', '2', '.'], ['4', '5', '6'], ['7', '8', '9']], (0, 0))
    ['1', '4', '7']
    >>> get_col([['1', '2', '3'], ['4', '.', '6'], ['7', '8', '9']], (0, 1))
    ['2', '.', '8']
    >>> get_col([['1', '2', '3'], ['4', '5', '6'], ['.', '8', '9']], (0, 2))
    ['3', '6', '9']
    """
    return [grid[i][pos[1]] for i in range(len(grid))]


def get_block(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.List[str]:
    """Возвращает все значения из квадрата, в который попадает позиция pos
    >>> grid = read_sudoku('puzzle1.txt')
    >>> get_block(grid, (0, 1))
    ['5', '3', '.', '6', '.', '.', '.', '9', '8']
    >>> get_block(grid, (4, 7))
    ['.', '.', '3', '.', '.', '1', '.', '.', '6']
    >>> get_block(grid, (8, 8))
    ['2', '8', '.', '.', '.', '5', '.', '7', '9']
    """
    a = []
    x = pos[0]
    y = pos[1]
    while x % 3 != 0:
        x -= 1
    while y % 3 != 0:
        y -= 1

    for i in range(x, x + int(len(grid) ** 0.25) + 2):
        for j in range(y, y + int(len(grid) ** 0.25) + 2):
            a.append(grid[i][j])
    return a


def find_empty_positions(grid: tp.List[tp.List[str]]) -> tp.Optional[tp.Tuple[int, int]]:
    """Найти первую свободную позицию в пазле
    >>> find_empty_positions([['1', '2', '.'], ['4', '5', '6'], ['7', '8', '9']])
    (0, 2)
    >>> find_empty_positions([['1', '2', '3'], ['4', '.', '6'], ['7', '8', '9']])
    (1, 1)
    >>> find_empty_positions([['1', '2', '3'], ['4', '5', '6'], ['.', '8', '9']])
    (2, 0)
    """
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == ".":
                return i, j
    return None


def find_possible_values(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.Set[str]:
    """Вернуть множество возможных значения для указанной позиции
    >>> grid = read_sudoku('puzzle1.txt')
    >>> values = find_possible_values(grid, (0,2))
    >>> values == {'1', '2', '4'}
    True
    >>> values = find_possible_values(grid, (4,7))
    >>> values == {'2', '5', '9'}
    True
    """
    possible_values = set()
    for i in range(1, 10):
        str_i = str(i)
        if str_i not in get_block(grid, pos) and str_i not in get_row(grid, pos) and str_i not in get_col(grid, pos):
            possible_values.add(str_i)
    return possible_values


import copy


def solve(grid: tp.List[tp.List[str]]) -> tp.Optional[tp.List[tp.List[str]]]:
    pos = find_empty_positions(grid)
    if not pos:
        return grid

    possible_values = find_possible_values(grid, pos)
    for value in possible_values:
        new_grid = copy.deepcopy(grid)  # Создаём копию перед изменением
        new_grid[pos[0]][pos[1]] = value
        result = solve(new_grid)
        if result:
            return result

    return None


def check_solution(solution: tp.List[tp.List[str]]) -> bool:
    """Если решение solution верно, то вернуть True, в противном случае False"""
    if find_empty_positions(solution):
        return False

    for i in range(9):
        row = get_row(solution, (i, 0))
        col = get_col(solution, (0, i))
        block = get_block(solution, (i // 3 * 3, i % 3 * 3))
        if len(set(row) - {"."}) != 9 or len(set(col) - {"."}) != 9 or len(set(block) - {"."}) != 9:
            return False
    return True


def generate_sudoku(N: int) -> tp.List[tp.List[str]]:
    """Генерация судоку заполненного на N элементов

    >>> grid = generate_sudoku(40)
    >>> sum(1 for row in grid for e in row if e == '.')
    41
    >>> solution = solve(grid)
    >>> check_solution(solution)
    True
    >>> grid = generate_sudoku(1000)
    >>> sum(1 for row in grid for e in row if e == '.')
    0
    >>> solution = solve(grid)
    >>> check_solution(solution)
    True
    >>> grid = generate_sudoku(0)
    >>> sum(1 for row in grid for e in row if e == '.')
    81
    >>> solution = solve(grid)
    >>> check_solution(solution)
    True
    """
    sudokuline = ["."] * 81
    sudoku = solve(group(sudokuline, 9))
    if sudoku is None:
        raise ValueError("valid sudoku")
    if N > 81:
        N = 81
    number_points = 81 - N
    for i in range(0, number_points):
        x = random.randrange(0, 9)
        y = random.randrange(0, 9)
        while sudoku[x][y] == ".":
            x = random.randrange(0, 9)
            y = random.randrange(0, 9)
        sudoku[x][y] = "."
    return sudoku


if __name__ == "__main__":
    for fname in ["puzzle1.txt", "puzzle2.txt", "puzzle3.txt"]:
        grid = read_sudoku(fname)
        display(grid)
        solution = solve(grid)
        if not solution:
            print(f"Puzzle {fname} can't be solved")
        else:
            display(solution)


def run_solve(filename: str) -> None:
    grid = read_sudoku(filename)
    start = time.time()
    solve(grid)
    end = time.time()
    print(f"{filename}: {end-start}")


if __name__ == "__main__":
    for filename in ("puzzle1.txt", "puzzle2.txt", "puzzle3.txt"):
        p = multiprocessing.Process(target=run_solve, args=(filename,))
        p.start()
