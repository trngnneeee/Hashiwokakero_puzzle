from helper import count_files_in_directory, read_file, print_result
from pysat_solution import solve_with_pysat
import os

INPUT_DIR = os.path.join(os.path.dirname(__file__), 'input')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')


def main():
    num_file = count_files_in_directory(INPUT_DIR)
    for i in range(num_file): 
        if (i == 9):
            input_path = os.path.join(INPUT_DIR, f'input-{i + 1}.txt')
        else: 
            input_path = os.path.join(INPUT_DIR, f'input-0{i + 1}.txt')
        output_path = os.path.join(OUTPUT_DIR, f'output{i}.txt')

        matrix = read_file(input_path)
        solution, islands, bridges = solve_with_pysat(matrix)
        print_result(matrix, islands, bridges, solution, output_path)

if __name__ == "__main__":
    main()
