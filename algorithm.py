from queue import PriorityQueue
from graph import Graph
from input import InputData
from math import sqrt, pow

# f: evalutate function, should takes in (grid, start pos, end pos, from node, to node)
# and return a tuple with the pure g(n) cost at [0] and the evaluated cost f(n) = g(n) + h(n) at [1]
def BestFirst(dat: InputData, grid: Graph, f) -> bool:
    prio_queue = PriorityQueue(grid.dim[0] * grid.dim[1])
    prio_queue.put((0, dat.start))
    if(grid.in_boundary(dat.start) == False or grid.in_boundary(dat.end) == False):
        pass
    grid.grid[grid.to_local_coord(dat.start)].visited = True
    grid.grid[grid.to_local_coord(dat.start)].cost = 0

    while(prio_queue.empty() == False):
        u = prio_queue.get()[1]
        node = grid.grid[grid.to_local_coord(u)]
        node.block = -1
        if(u[0] == dat.end[0] and u[1] == dat.end[1]):          # for UCS, this statement is necessary
            return True                                         # in order to convert to Dijkstra, do not stop at the goal
        for i in range(-1, 2):
            for j in range(-1, 2):
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
                if(cond):
                    fn = f(grid, dat.start, dat.end, u, new_dest)
                    prio_queue.put((fn[1], new_dest))
                    local = grid.to_local_coord(new_dest)
                    grid.grid[local].block = -10
                    grid.grid[local].visited = True
                    grid.grid[local].from_node = u
                    grid.grid[local].cost = fn[0]
    return False

def BFS(dat: InputData, grid: Graph) -> bool:
    def eval(grid: Graph, s, e, u, n):
        return (0, 0) # cost = 0 for all,
                      # we should have f(n) = depth, since we are putting frontierees in a priority queue
                      # but because this is a queue, it inherits the property of FIFO, so uniform f(n) elements
                      # should work like a normal queue, which is fine for BFS
    return BestFirst(dat, grid, eval)

def UCS(dat: InputData, grid: Graph) -> bool:
    def eval(grid: Graph, s, e, u, n):
        d_x = abs(u[0] - n[0])
        d_y = abs(u[1] - n[1])
        mod = 1
        if(d_x == d_y and d_x != 0):
            mod = 1.5   # 1.4 should be closer, and should be choose on large maps
                        # 1.5 is Okay on small maps, but will introduce a diverted error, 
        g = grid.grid[grid.to_local_coord(u)].cost + mod
        return (g, g)
    return BestFirst(dat, grid, eval)
    

def Astar(dat: InputData, grid: Graph) -> bool:
    def eval(grid: Graph, s, e, u, n):
        d_x = abs(u[0] - n[0])
        d_y = abs(u[1] - n[1])
        mod = 1
        if(d_x == d_y and d_x != 0):
            mod = 1.5   # 1.4 should be closer, and should be choose on large maps
                        # 1.5 is Okay on small maps, but will introduce a diverted error, 
        g = grid.grid[grid.to_local_coord(u)].cost + mod

        dist_x = n[0] - e[0]
        dist_y = n[1] - e[1]
        # h = abs(dist_x) + abs(dist_y)   Manhanttan distance, not feasible for diagonal movement-allowed actions.
        h = sqrt(pow(abs(dist_x), 2) + pow(abs(dist_y), 2))   # Pythagorean distance, much more feasible
        return (g, h + g)
    return BestFirst(dat, grid, eval)
