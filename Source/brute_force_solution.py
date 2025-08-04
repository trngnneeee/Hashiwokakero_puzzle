from pysat.formula import CNF, IDPool
import itertools
from helper import get_island_info, generate_bridge, add_main_contraints, add_island_contraints, add_non_crossing_constraints, check_connect, get_n_vars, interpret_model
import time
import tracemalloc

def solve_with_brute_force(matrix):
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

    for c in itertools.product([False, True], repeat=n):
        assignment = [None] + list(c)
        satisfied = True

        for clause in clauses:
            if not any((lit > 0 and assignment[abs(lit)]) or
                       (lit < 0 and not assignment[abs(lit)]) for lit in clause):
                satisfied = False
                break

        if satisfied:
            solution = interpret_model(assignment, bridge_vars)
            if check_connect(solution, islands):
                elapsed = time.perf_counter() - start_time
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                return solution, islands, bridges, elapsed, peak / 1024

    elapsed = time.perf_counter() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return None, None, None, elapsed, peak / 1024
