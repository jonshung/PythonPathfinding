from queue import PriorityQueue
from graph import Graph
from input import InputData
from math import sqrt, pow
import copy

# f: evalutate function, should takes in (grid, start pos, end pos, from node, to node)
# and return a tuple with the pure g(n) cost at [0] and the evaluated cost f(n) = g(n) + h(n) at [1]
# evalOrder: the order in which goal test is applied. 0 = when expanding, 1 = when generating
def BestFirst(dat: InputData, grid: Graph, f, evalOrder=0) -> bool:
    # premature check
    if(grid.grid[grid._to_local_coord(dat.start[0], dat.start[1])].block >= -0 or \
       grid.grid[grid._to_local_coord(dat.start[0], dat.start[1])].block >= 0):
        return False
    
    prio_queue = PriorityQueue(grid.dim[0] * grid.dim[1])
    prio_queue.put((0, dat.start))
    if(grid.in_boundary(dat.start) == False or grid.in_boundary(dat.end) == False):
        return False
    grid.grid[grid.to_local_coord(dat.start)].visited = True
    grid.grid[grid.to_local_coord(dat.start)].cost = 0

    while(prio_queue.empty() == False):
        u = prio_queue.get()[1]
        node = grid.grid[grid.to_local_coord(u)]
        if(node.visited and node.block == -1):
            continue
        node.block = -1
        
        if(evalOrder == 0 and u[0] == dat.end[0] and u[1] == dat.end[1]):          # for UCS, this statement is necessary
            return True                                         # in order to convert to Dijkstra, do not stop at the goal
        for i in range(-1, 2):
            for j in range(1, -2, -1):
                adjx = u[0] + i
                adjy = u[1] + j
                new_dest = [adjx, adjy]
                cond = False

                if(abs(i) == abs(j)):
                    if(grid.can_move_diagonal(u, new_dest)):
                        cond = True
                else:
                    if(grid.can_move_straight(new_dest)):
                        cond = True
                if(cond == False):
                    continue

                id = grid.to_local_coord(new_dest)
                new_node = grid.grid[id]
                fn = f(grid, dat.start, dat.end, u, new_dest)

                if(new_node.visited == False or (new_node.block == -10 and new_node.cost > fn[0])):
                    new_node.visited = True
                    new_node.block = -10
                    new_node.from_node = u
                    new_node.cost = fn[0]
                    if(evalOrder == 1 and new_dest[0] == dat.end[0] and new_dest[1] == dat.end[1]):          # node generation goal test
                        new_node.block = -1
                        return True
                    prio_queue.put((fn[1], new_dest))

    return False

def BFS(dat: InputData, grid: Graph) -> bool:
    def eval(grid: Graph, s, e, u, n):
        d_x = abs(u[0] - n[0])
        d_y = abs(u[1] - n[1])
        mod = 1
        if(d_x == d_y and d_x != 0):
            mod = 1.41
        g = grid.grid[grid.to_local_coord(u)].cost + mod
        return (g, 0) # cost = 0 for all,
                      # we should have f(n) = depth, since we are putting frontierees in a priority queue
                      # but because this is a queue, it inherits the property of FIFO, so uniform f(n) elements
                      # should work like a normal queue, which is fine for BFS
    return BestFirst(dat, grid, eval, 1)

def DFS(dat: InputData, grid: Graph) -> bool:
    # premature check
    if(grid.grid[grid._to_local_coord(dat.start[0], dat.start[1])].block >= -0 or \
       grid.grid[grid._to_local_coord(dat.start[0], dat.start[1])].block >= 0):
        return False
    
    movestack = []
    movestack.append(dat.start)
    
    start_node = grid.grid[grid._to_local_coord(dat.start[0], dat.start[1])]
    start_node.block = -1
    start_node.visited = True
    start_node.cost = 0

    while len(movestack) > 0:
        u = movestack.pop()
        node = grid.grid[grid.to_local_coord(u)]
        node.block = -1
        for i in range(-1, 2):
            for j in range(1, -2, -1):
                adjx = u[0] + j
                adjy = u[1] + i
                new_dest = [adjx, adjy]
                cond = False

                if(abs(i) == abs(j)):
                    if(grid.can_move_diagonal(u, new_dest)):
                        cond = True
                else:
                    if(grid.can_move_straight(new_dest)):
                        cond = True

                id = grid.to_local_coord(new_dest)
                new_node = grid.grid[id]

                if(cond and new_node.visited == False):
                    new_node.visited =  True
                    new_node.block = -10
                    new_node.from_node = u
                    
                    d_x = abs(u[0] - new_dest[0])
                    d_y = abs(u[1] - new_dest[1])
                    mod = 1
                    if(d_x == d_y and d_x != 0):
                        mod = 1.41
                    g = grid.grid[grid.to_local_coord(u)].cost + mod

                    new_node.cost = g
                    if(new_dest[0] == dat.end[0] and new_dest[1] == dat.end[1]):
                        new_node.block = -1
                        return True
                    movestack.append(new_dest)
    return False

# Same as BFS because the distance when travelling between nodes are relatively the same (except for diagonal movement)
# thus algorithm expands frontier as depth-like waves
def UCS(dat: InputData, grid: Graph) -> bool:
    def eval(grid: Graph, s, e, u, n):
        d_x = abs(u[0] - n[0])
        d_y = abs(u[1] - n[1])
        mod = 1
        if(d_x == d_y and d_x != 0):
            mod = 1.41
        g = grid.grid[grid.to_local_coord(u)].cost + mod
        return (g, g)
    return BestFirst(dat, grid, eval)

def GreedyBFS(dat: InputData, grid: Graph) -> bool:
    def eval(grid: Graph, s, e, u, n):
        d_x = abs(u[0] - n[0])
        d_y = abs(u[1] - n[1])
        mod = 1
        if(d_x == d_y and d_x != 0):
            mod = 1.41
        g = grid.grid[grid.to_local_coord(u)].cost + mod

        dist_x = n[0] - e[0]
        dist_y = n[1] - e[1]
        # h = abs(dist_x) + abs(dist_y)   Manhanttan distance, not feasible for diagonal movement-allowed actions.
        h = sqrt(pow(abs(dist_x), 2) + pow(abs(dist_y), 2))   # Pythagorean distance, much more feasible
        return (g, h)
    return BestFirst(dat, grid, eval)

def Dijkstra(dat: InputData, grid: Graph) -> bool:
    def eval(grid: Graph, s, e, u, n): # same eval as UCS but wont stop at goal
        d_x = abs(u[0] - n[0])
        d_y = abs(u[1] - n[1])
        mod = 1
        if(d_x == d_y and d_x != 0):
            mod = 1.41
        g = grid.grid[grid.to_local_coord(u)].cost + mod
        return (g, g)
    return BestFirst(dat, grid, eval, 2) # eval pos = 2 will cause the algorithm to run forever, until no more node is to be expanded

def Astar(dat: InputData, grid: Graph) -> bool:
    def eval(grid: Graph, s, e, u, n):
        d_x = abs(u[0] - n[0])
        d_y = abs(u[1] - n[1])
        mod = 1
        if(d_x == d_y and d_x != 0):
            mod = 1.41                  # 1.5 overestimate diagonal movement, might result in unwanted movement
        g = grid.grid[grid.to_local_coord(u)].cost + mod

        dist_x = n[0] - e[0]
        dist_y = n[1] - e[1]
        # h = abs(dist_x) + abs(dist_y)   Manhanttan distance, not feasible for diagonal movement-allowed actions.
        h = sqrt(pow(abs(dist_x), 2) + pow(abs(dist_y), 2))   # Pythagorean distance, much more feasible
        return (g, h + g)
    return BestFirst(dat, grid, eval)