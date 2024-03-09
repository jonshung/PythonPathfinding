
from input import InputData
from graph import Graph
from algorithm import Dijkstra, Astar
import itertools
import copy

def MinCostSet(dat: InputData, grid: Graph) -> list:
    # atleast NP-intermediate, could be NP-hard
    cost = [] # cost from node i -> j
    
    checkpoints = [dat.start]
    for x in dat.pickup:
        checkpoints.append(x)
    checkpoints.append(dat.end)

    i = 0
    for node in checkpoints:
        dat2 = copy.deepcopy(dat)
        dat2.start = node

        grid.partial_reset()
        node_queue = []
        Dijkstra(dat2, grid)

        # put all visiting checkpoints in queue
        for node_2 in checkpoints:
            if(node_2 == node):
                continue
            node_queue.append(grid.grid[grid.to_local_coord(node_2)].cost)
        # put end in queue
        node_queue.insert(i, 0)
        i += 1
        cost.append(node_queue)
    
    return cost
        
# https://github.com/CarlEkerot/held-karp
def held_karp(dists):
    """
    Implementation of Held-Karp, an algorithm that solves the Traveling
    Salesman Problem using dynamic programming with memoization.

    Parameters:
        dists: distance matrix

    Returns:
        A tuple, (cost, path).
    """
    n = len(dists)

    # Maps each subset of the nodes to the cost to reach that subset, as well
    # as what node it passed before reaching this subset.
    # Node subsets are represented as set bits.
    C = {}

    # Set transition cost from initial state
    for k in range(1, n):
        C[(1 << k, k)] = (dists[0][k], 0)

    # Iterate subsets of increasing length and store intermediate results
    # in classic dynamic programming manner
    for subset_size in range(2, n):
        for subset in itertools.combinations(range(1, n), subset_size):
            # Set bits for all nodes in this subset
            bits = 0
            for bit in subset:
                bits |= 1 << bit

            # Find the lowest cost to get to this subset
            for k in subset:
                prev = bits & ~(1 << k)

                res = []
                for m in subset:
                    if m == 0 or m == k:
                        continue
                    res.append((C[(prev, m)][0] + dists[m][k], m))
                C[(bits, k)] = min(res)

    # We're interested in all bits but the least significant (the start state)
    bits = (2**n - 1) - 1

    # Calculate optimal cost
    res = []
    for k in range(1, n):
        res.append((C[(bits, k)][0], k))
    opt, parent = min(res)

    # Backtrack to find full path
    path = []
    for i in range(n - 1):
        path.append(parent)
        new_bits = bits & ~(1 << parent)
        _, parent = C[(bits, parent)]
        bits = new_bits

    # Add implicit start state
    path.append(0)

    return opt, list(reversed(path))

def reconstruct_path(dat: InputData, grid: Graph, order: list) -> bool:
    checkpoints = [dat.start]
    for x in dat.pickup:
        checkpoints.append(x)
    checkpoints.append(dat.end)

    path = []
    starting_cost = 0
    grid.partial_reset()

    for i in range(len(order)):
        if(i == (len(order) - 1)):
            continue
        start = checkpoints[order[i]]
        end = checkpoints[order[i +  1]]
        dat2 = copy.deepcopy(dat)

        dat2.start = start
        dat2.end = end
        if(Astar(dat2, grid) == False):
            return False

        t_path = []
        traceback = dat2.end
        while(grid.in_boundary(traceback)):
            n_node = grid.grid[grid.to_local_coord(traceback)]
            t_path.append((round(starting_cost + n_node.cost, 2), traceback))
            traceback = n_node.from_node
        t_path.reverse()
        path.extend(t_path)
        
        starting_cost += grid.grid[grid.to_local_coord(dat2.end)].cost
        grid.partial_reset()
    
    for node_i in range(len(path)):
        node_data = path[node_i]
        tgt = grid.grid[grid.to_local_coord(node_data[1])]
        tgt.visited = True
        tgt.block = -1
        tgt.cost = node_data[0]
        if(node_i > 0):
            if(path[node_i - 1][1] != node_data[1]):
                tgt.from_node = path[node_i - 1][1]
    return True

def tsp(dat: InputData, grid: Graph):
    set_cost = MinCostSet(dat, grid)
    algo_res = held_karp(set_cost)
    res = reconstruct_path(dat, grid, algo_res[1])
    if res:
        grid.grid[grid.to_local_coord(dat.end)].cost = algo_res[0]
        return True
    else:
        return False