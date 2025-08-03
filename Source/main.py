from helper import count_files_in_directory, read_file, count_possible_bridges
from pysat_solution import solve_with_pysat
import os

from backtrack_solution import solve_with_back_track

INPUT_DIR = os.path.join(os.path.dirname(__file__), 'input')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

def print_result(matrix, islands, solution):
    """ 
    Print the result in a readable format.
    """
    rows = len(matrix)
    cols = len(matrix[0])
    output = [['0' for _ in range(cols)] for _ in range(rows)]

    island_positions = {}
    for id, (r, c, req) in islands.items():
        output[r][c] = str(req)
        island_positions[id] = (r, c)
    for (i, j), count in solution.items():
        r1, c1 = island_positions[i]
        r2, c2 = island_positions[j]
        if r1 == r2:
            r = r1
            for c in range(min(c1, c2) + 1, max(c1, c2)):
                output[r][c] = '-' if count == 1 else '='
        elif c1 == c2:
            c = c1
            for r in range(min(r1, r2) + 1, max(r1, r2)):
                output[r][c] = '|' if count == 1 else '$'

    for row in output:
        print(' '.join(row))

def main():
    num_file = count_files_in_directory(INPUT_DIR)
    for idx in range(num_file): 
        if (idx == 9):
            input_path = os.path.join(INPUT_DIR, f'input-{idx + 1}.txt')
        else: 
            input_path = os.path.join(INPUT_DIR, f'input-0{idx + 1}.txt')
        output_path = os.path.join(OUTPUT_DIR, f'output{idx + 1}.txt')

        matrix = read_file(input_path)
        #check 
        with open(output_path, 'w') as fout:
            for i in range(len(matrix)):
                for j in range(len(matrix[0])):
                    if matrix[i][j] > 0:
                        possible = count_possible_bridges(matrix, i, j)
                        if possible < matrix[i][j]:
                            fout.write(f"Island at ({i},{j}) requires {matrix[i][j]} bridges but only {possible} possible solution\n")

        solution, islands, bridges = solve_with_back_track(matrix)
        if solution is None:
            with open(output_path, 'at') as fout:
                fout.write(f'No solution for input-{idx + 1}.txt\n')
            continue 
        print_result(matrix, islands, solution, output_path)

if __name__ == "__main__":
    main()
