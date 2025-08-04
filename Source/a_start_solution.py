import heapq
import time
from pysat.formula import CNF, IDPool
import tracemalloc
from helper import (
    get_island_info, generate_bridge,
    add_main_contraints, add_island_contraints, 
    add_non_crossing_constraints, check_connect,
    get_n_vars, interpret_model
)

def solve_with_a_star(matrix):
    """
    Solve Hashiwokakero applying A* algorithm and measure time.
    """
    start_time = time.perf_counter()
    tracemalloc.start() 

    islands = get_island_info(matrix)
    bridges, coord_to_id = generate_bridge(islands, matrix)

    cnf = CNF()
    vpool = IDPool()

    bridge_vars = add_main_contraints(cnf, vpool, bridges)
    add_island_contraints(cnf, vpool, islands, bridge_vars)
    add_non_crossing_constraints(cnf, vpool, bridges)

    clauses = cnf.clauses
    n = get_n_vars(cnf)
    init = [None] * (n + 1)

    def heuristic(assgn):
        h = 0
        for clause in clauses:
            sat = False
            for lit in clause:
                if assgn[abs(lit)] is None:
                    sat = True
                    break
                elif (lit > 0 and assgn[abs(lit)] is True) or (lit < 0 and assgn[abs(lit)] is False):
                    sat = True
                    break
            if not sat:
                h += 1
        return h

    g0 = 0
    h0 = heuristic(init)
    open_heap = []
    heapq.heappush(open_heap, (g0 + h0, g0, init))
    closed = set()

    while open_heap:
        f, g, assgn = heapq.heappop(open_heap)
        state_key = tuple(assgn)
        if state_key in closed:
            continue
        closed.add(state_key)

        if None not in assgn[1:]:
            valid = True
            for clause in clauses:
                if not any(
                    (lit > 0 and assgn[abs(lit)] is True) or 
                    (lit < 0 and assgn[abs(lit)] is False)
                    for lit in clause
                ):
                    valid = False
                    break
            if valid:
                solution = interpret_model(assgn, bridge_vars)
                if check_connect(solution, islands):
                    elapsed = time.perf_counter() - start_time
                    current, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    return solution, islands, bridges, elapsed, peak / 1024
            continue

        try:
            i = assgn.index(None, 1)
        except ValueError:
            i = None
        if i is None:
            continue

        for val in [False, True]:
            new_assgn = assgn.copy()
            new_assgn[i] = val

            # Early conflict check
            conflict = False
            for clause in clauses:
                sat = False
                unassigned = False
                for lit in clause:
                    if new_assgn[abs(lit)] is None:
                        unassigned = True
                        continue
                    elif (lit > 0 and new_assgn[abs(lit)] is True) or (lit < 0 and new_assgn[abs(lit)] is False):
                        sat = True
                        break
                if not sat and not unassigned:
                    conflict = True
                    break
            if conflict:
                continue

            new_g = g + 1
            new_h = heuristic(new_assgn)
            heapq.heappush(open_heap, (new_g + new_h, new_g, new_assgn))

    elapsed = time.perf_counter() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return None, None, None, elapsed, peak / 1024 
