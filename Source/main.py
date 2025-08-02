from helper import print_result
from pysat_solution import solve_with_pysat
from a_start_solution import solve_with_a_star
from brute_force_solution import solve_with_brute_force

matrix = [
    [0, 2, 0, 5, 0, 0, 2],
    [0, 0, 0, 0, 0, 0, 0],
    [4, 0, 2, 0, 2, 0, 4],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 5, 0, 2, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [4, 0, 0, 0, 0, 0, 3]
]

def main():
    solution, islands, bridges = solve_with_a_star(matrix)
    print_result(matrix, islands, solution)

if __name__ == "__main__":
    main()
