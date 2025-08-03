from pysat.card import CardEnc
import os

def get_island_info(matrix):
    """
    Get the island dictionary
      Input: Matrix
      Output: Dictionary: {island_id -> (row, col, required_bridges_number)}
    """
    islands = {}
    island_id = 1
    for i, row in enumerate(matrix):
        for j, cell in enumerate(row):
            if cell != 0:
                islands[island_id] = (i, j, cell)
                island_id += 1
    return islands

def generate_bridge(islands, matrix):
    """
      Find all possible connection between 2 island
      Input: islands, matrix
      Output: edges: List of tuple (island_id_1, island_id_2, extra), extra represent how 2 island is connect. Ex: ('horizontal', row_index, start_col_index, end_col_index) ('vertical', col_index, start_row_index, end_row_index)
    """
    bridges = []
    coord_to_id = {}
    for id, (r, c, required_bridge) in islands.items():
        coord_to_id[(r, c)] = id

    row = len(matrix)
    col = len(matrix[0])

    for id, (r, c, required_bridge) in islands.items():
        # Find bridge for each row
        for next_c in range(c + 1, col):
            if (r, next_c) in coord_to_id:
                valid = True
                for tmpC in range(c + 1, next_c):
                    if (matrix[r][tmpC] != 0):
                        valid = False
                        break
                if valid:
                    id2 = coord_to_id[(r, next_c)]
                    bridge = tuple(sorted((id, id2)))
                    bridges.append( (bridge, ('horizontal', r, c, next_c)) )
                break
        # Find bridge for each col
        for next_r in range(r + 1, row):
            if (next_r, c) in coord_to_id:
                valid = True
                for tmpR in range(r + 1, next_r):
                    if (matrix[tmpR][c] != 0):
                        valid = False
                        break
                if valid:
                    id2 = coord_to_id[(next_r, c)]
                    bridge = tuple(sorted((id, id2)))
                    bridges.append((bridge, ('vertical', c, r, next_r)))
                break
            
    # Remove duplicate bridge
    unique_bridge = {}
    for (bridge, extra) in bridges:
        if bridge not in unique_bridge:
            unique_bridge[bridge] = extra
    res = [(bridge[0], bridge[1], extra) for bridge, extra in unique_bridge.items()]
    return res, coord_to_id

def add_main_contraints(cnf, vpool, bridges):
    """
    Constraint: If there are 2 bridge between 2 island, there is at least 1 bridge between them.
    For each bridge, if there is a x2 bridge with 2 line, there is at least 1 bridge x1 with 1 line
    """
    bridge_vars = {}
    for (i, j, extra) in bridges:
        x1 = vpool.id(('x', i, j, 1))
        x2 = vpool.id(('x', i, j, 2))
        cnf.append([-x2, x1])
        bridge_vars[(i, j)] = (x1, x2)
    return bridge_vars

def add_island_contraints(cnf, vpool, islands, bridge_vars):
    """
    Constraint: For each island, the total number of bridge link to it equal its value.
    """
    required_bridge = {id: [] for id in islands.keys()}
    for (i, j), (x1, x2) in bridge_vars.items():
        if i in required_bridge:
            required_bridge[i].extend([x1, x2])
        if j in required_bridge:
            required_bridge[j].extend([x1, x2])
    for id, lits in required_bridge.items():
        require = islands[id][2]
        if len(lits) >= require and require > 0:
            card = CardEnc.equals(lits=lits, bound=require, vpool=vpool, encoding=1)
            cnf.extend(card.clauses)
        elif require == 0:
            for lit in lits:
                cnf.append([-lit])
        else:
            cnf.append([])
    return

def count_possible_bridges(grid, row, col):
    R, C = len(grid), len(grid[0])
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
    count = 0
    for dr, dc in directions:
        r, c = row + dr, col + dc
        while 0 <= r < R and 0 <= c < C:
            if grid[r][c] > 0:
                count += 1
                break
            elif grid[r][c] == 0:
                r += dr
                c += dc
            else:
                break
    return count

def add_non_crossing_constraints(cnf, vpool, bridges):
    """
    There are no vertical and horizontal bridge cross.
    """
    bridge_list = [((i, j), extra) for (i, j, extra) in bridges]
    n = len(bridge_list)

    for i in range(n):
        (bridge1, extra1) = bridge_list[i]
        for j in range(i + 1, n):
            (bridge2, extra2) = bridge_list[j]
            if extra1[0] == 'horizontal' and extra2[0] == 'vertical':
                r = extra1[1]
                start_c, end_c = extra1[2], extra1[3]
                c = extra2[1]
                start_r, end_r = extra2[2], extra2[3]
                if start_r < r < end_r and start_c < c < end_c:
                    x1_e1 = vpool.id(('x', bridge1[0], bridge1[1], 1))
                    x1_e2 = vpool.id(('x', bridge2[0], bridge2[1], 1))
                    cnf.append([-x1_e1, -x1_e2])
            elif extra1[0] == 'vertical' and extra2[0] == 'horizontal':
                r = extra2[1]
                start_c, end_c = extra2[2], extra2[3]
                c = extra1[1]
                start_r, end_r = extra1[2], extra1[3]
                if start_r < r < end_r and start_c < c < end_c:
                    x1_e1 = vpool.id(('x', bridge1[0], bridge1[1], 1))
                    x1_e2 = vpool.id(('x', bridge2[0], bridge2[1], 1))
                    cnf.append([-x1_e1, -x1_e2])
    return

def check_connect(solution, islands):
    """
    Check all the island is connect using DFS.
    """
    # Init adjacency list
    graph = {i: [] for i in islands.keys()}
    for (i, j), count in solution.items():
        if count > 0:
            graph[i].append(j)
            graph[j].append(i)
    visited = set()

    def dfs(u):
        visited.add(u)
        for v in graph[u]:
            if v not in visited:
                dfs(v)
    
    start = min(islands.keys())
    dfs(start)
    return len(visited) == len(islands)

def get_n_vars(cnf):
    """
    Get the number of variables in the CNF formula.
    This is the maximum absolute value of the literals in the clauses.  
    """
    n = 0
    for clause in cnf.clauses:
        for lit in clause:
            n = max(n, abs(lit))
    return n

def interpret_model(assignment, bridge_vars):
    """ 
    Interpret the model to get the solution in a readable format.
    Input: assignment (list of boolean values), bridge_vars): (dictionary of edge variables)
    Output: solution (dictionary of edges with their counts)
    """
    sol = {}
    for key, (x1, x2) in bridge_vars.items():
        if assignment[x1]:
            count = 1
            if assignment[x2]:
                count = 2
            sol[key] = count
    return sol

def read_file(filename): 
    matrix = []
    with open(filename, 'r') as file:
        for line in file: 
            r = list(map(int, line.strip().split(', ')))
            matrix.append(r)
    return matrix

def print_result(matrix, islands, solution, filename):
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

    with open(filename, 'w') as f:
        for r in output: 
            f.write(' '.join(r) + '\n')

def count_files_in_directory(folder_path):
    count = 0
    for entry in os.listdir(folder_path):
        full_path = os.path.join(folder_path, entry)
        if os.path.isfile(full_path):
            count += 1
    return count