from pysat.formula import CNF, IDPool
from helper import (
    get_island_info, generate_bridge,
    add_main_contraints, add_island_contraints, add_non_crossing_constraints,
    check_connect, get_n_vars, interpret_model
)
import time
import tracemalloc

def solve_with_back_track(matrix):
    tracemalloc.start()
    start_time = time.perf_counter()

    islands = get_island_info(matrix)
    bridges, coord_to_id = generate_bridge(islands, matrix)

    cnf = CNF()
    vpool = IDPool()

    bridge_vars = add_main_contraints(cnf, vpool, bridges)
    add_island_contraints(cnf, vpool, islands, bridge_vars)
    add_non_crossing_constraints(cnf, vpool, bridges)

    clauses = cnf.clauses
    n = get_n_vars(cnf)

    def is_valid(assignment):
        for clause in clauses:
            satisfied = False
            for lit in clause:
                val = assignment[abs(lit)]
                if val is None:
                    satisfied = True
                    break
                elif (lit > 0 and val is True) or (lit < 0 and val is False):
                    satisfied = True
                    break
            if not satisfied:
                return False
        return True

    def backtrack(assignment, i=1):
        if i > n:
            if is_valid(assignment):
                solution = interpret_model(assignment, bridge_vars)
                if check_connect(solution, islands):
                    return solution
            return None

        for val in [False, True]:
            assignment[i] = val
            if is_valid(assignment):
                result = backtrack(assignment, i + 1)
                if result:
                    return result
            assignment[i] = None
        return None

    assignment = [None] * (n + 1)
    solution = backtrack(assignment)
    
    elapsed = time.perf_counter() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if solution:
        return solution, islands, bridges, elapsed, peak / 1024
    else:
        return None, None, None, elapsed, peak / 1024