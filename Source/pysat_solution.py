import time
import tracemalloc
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver
from helper import (
    get_island_info, generate_bridge,
    add_main_contraints, add_island_contraints, 
    add_non_crossing_constraints, check_connect
)

def solve_with_pysat(matrix):
    tracemalloc.start()
    start_time = time.perf_counter()

    islands = get_island_info(matrix)
    bridges, coor_to_id = generate_bridge(islands, matrix)

    cnf = CNF()
    vpool = IDPool()

    bridge_vars = add_main_contraints(cnf, vpool, bridges)
    add_island_contraints(cnf, vpool, islands, bridge_vars)
    add_non_crossing_constraints(cnf, vpool, bridges)

    solver = Solver(name='glucose3')
    solver.append_formula(cnf)

    while solver.solve():
        model = solver.get_model()
        solution = {}
        used_literals = []

        for (i, j), (x1, x2) in bridge_vars.items():
            if model[x1 - 1] > 0:
                count = 1
                if model[x2 - 1] > 0:
                    count = 2
                solution[(i, j)] = count
                used_literals.append(x1)

        if check_connect(solution, islands):
            solver.delete()
            elapsed = time.perf_counter() - start_time
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            return solution, islands, bridges, elapsed, peak / 1024
        else:
            solver.add_clause([-lit for lit in used_literals])

    solver.delete()
    elapsed = time.perf_counter() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return None, None, None, elapsed, peak / 1024