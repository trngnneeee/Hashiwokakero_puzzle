from helper import count_files_in_directory, read_file, count_possible_bridges, print_result, measure_time
from pysat_solution import solve_with_pysat
import os
from backtrack_solution import solve_with_back_track
from a_start_solution import solve_with_a_star
from brute_force_solution import solve_with_brute_force

INPUT_DIR = os.path.join(os.path.dirname(__file__), 'input')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

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

        solution, islands, bridges = solve_with_pysat(matrix)
        if solution is None:
            with open(output_path, 'at') as fout:
                fout.write(f'No solution for input-{idx + 1}.txt\n')
            continue 
        print_result(matrix, islands, solution, output_path)

        #measure performance 
        time = measure_time(solve_with_pysat, matrix)
        print(f"Time: {time:.4f}s")

if __name__ == "__main__":
    main()
