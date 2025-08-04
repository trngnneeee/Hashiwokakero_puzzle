from helper import count_files_in_directory, read_file, count_possible_bridges, print_result
from pysat_solution import solve_with_pysat
from backtrack_solution import solve_with_back_track
from a_start_solution import solve_with_a_star
from brute_force_solution import solve_with_brute_force
import os

INPUT_DIR = os.path.join(os.path.dirname(__file__), 'input')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

def main():
    num_files = count_files_in_directory(INPUT_DIR)
    for idx in range(num_files): 
        file_name = f'input-{idx + 1}.txt' if idx >= 9 else f'input-0{idx + 1}.txt'
        input_path = os.path.join(INPUT_DIR, file_name)
        output_path = os.path.join(OUTPUT_DIR, f'output{idx + 1}.txt')

        print(f'\nProcessing file: {file_name}')
        print("Choose a solving method:")
        print("1. A*")
        print("2. Backtracking")
        print("3. Brute-force")
        print("4. pySAT")
        print("5. Run all methods")
        
        choice = input("Enter your choice (1-5): ").strip()

        matrix = read_file(input_path)

        with open(output_path, 'w') as fout:
            for i in range(len(matrix)):
                for j in range(len(matrix[0])):
                    if matrix[i][j] > 0:
                        possible = count_possible_bridges(matrix, i, j)
                        if possible < matrix[i][j]:
                            fout.write(f"Island at ({i},{j}) requires {matrix[i][j]} bridges but only {possible} possible.\n")

        methods = {
            "1": ("A*", solve_with_a_star),
            "2": ("Backtracking", solve_with_back_track),
            "3": ("Brute-force", solve_with_brute_force),
            "4": ("pySAT", solve_with_pysat),
        }

        results = []

        if choice == "5":
            for name, func in methods.values():
                try:
                    solution, islands, bridges, t, mem = func(matrix)
                    print(f"{name}: {t:.4f}s | {mem:.2f} KB")
                    if solution is None:
                        print(f"{name}: No solution found.")
                    else:
                        results.append((name, solution, islands, bridges, t, mem))
                except Exception as e:
                    print(f"{name} failed: {e}")
        elif choice in methods:
            name, func = methods[choice]
            try:
                solution, islands, bridges, t, mem = func(matrix)
                print(f"{name}: {t:.4f}s | {mem:.2f} KB")
                if solution is None:
                    print(f"{name}: No solution found.")
                else:
                    results.append((name, solution, islands, bridges, t, mem))
            except Exception as e:
                print(f"{name} failed: {e}")
        else:
            print("Invalid choice. Skipping this file.")
            continue

        if not results:
            with open(output_path, 'a') as fout:
                fout.write(f'No solution found for {file_name}\n')
        else:
            best = min(results, key=lambda x: x[4])  
            print_result(matrix, best[2], best[1], output_path)

if __name__ == "__main__":
    main()
