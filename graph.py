from sys import maxsize

class Node:
    block: int = -9 # 0 -> +inf: geometry, -1: node on result path, -9: open node, -10: expanded but not visited
    anchor: bool = False
    cost: float = maxsize       # depends on the algorithm, for BestFirsts', it is the PATH-COST, i.e cost from start -> current node
    visited = False             # trivial property for reached state 
    from_node = [-1, -1]        # coordinate of parent node

    def __repr__(self) -> str:
        return str(self.block)

    def __init__(self, cost_vl, block_vl) -> None:
        self.cost = cost_vl
        self.block = block_vl

class Graph:
    grid: list[Node]            # a M x N, 1D array containing informations of each node
    dim: list[int]              # dimension, dim[0] = x, dim[1] = y
    geo_size: int = 0           # number of geometries on the graph

    def __repr__(self) -> str:
        stri = ""
        n = self.dim[0] + 1
        for i in range(0, len(self.grid), n):
            stri += str(self.grid[i:i+n])
            stri += "\n"
        return stri

    def __init__(self, dim_vl: list[int], geo_size_vl: int, geo_data_vl: list[list[list[int]]]) -> None:
        self.dim = dim_vl
        self.dim[0] += 1
        self.dim[1] += 1
        for i in range(len(self.dim)):
            if self.dim[i] <= 0:
                self.dim[i] = 1
        self.geo_size = geo_size_vl
        self.construct(geo_size_vl, geo_data_vl)

    def _to_local_coord(self, x: int, y: int) -> int:
        return x % (self.dim[0]) + y * (self.dim[0])
    
    def to_local_coord(self, pos: list[int]) -> int:
        if(len(pos) < 2):
            return -1
        return self._to_local_coord(pos[0], pos[1])
    
    def _in_boundary(self, x: int, y: int) -> bool:
        return (x > 0 and x < (self.dim[0] - 1)) and (y > 0 and y < (self.dim[1] - 1))
    
    def in_boundary(self, pos: list[int]) -> bool:
        if(len(pos) < 2):
            return False
        return self._in_boundary(pos[0], pos[1])
    
    def _can_move_straight(self, x: int, y: int) -> bool:
        local = self._to_local_coord(x, y)
        return  self._in_boundary(x, y) and self.grid[local].visited == False and self.grid[local].block <= -9
    
    def can_move_straight(self, pos: list[int]) -> bool:
        if(len(pos) < 2):
            return False
        return self._can_move_straight(x=pos[0], y=pos[1])
    
    def _can_move_diagonal(self, from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        if(self._in_boundary(to_x, to_y) == False):
            return False
        #check going through wall
        unblocked = (self.grid[self._to_local_coord(to_x, to_y)].block <= -9) and \
                    (self.grid[self._to_local_coord(from_x, to_y)].block <= -9) and \
                    (self.grid[self._to_local_coord(to_x, from_y)].block <= -9)
        return self.grid[self._to_local_coord(to_x, to_y)].visited == False and unblocked
    
    def can_move_diagonal(self, from_pos: list[int], to_pos: list[int]) -> bool:
        if(len(from_pos) < 2 or len(to_pos) < 2):
            return False
        return self._can_move_diagonal(from_pos[0], from_pos[1], to_pos[0], to_pos[1])
    
    def line(self, i: int, dist_x: int, dist_y: int, dest: list):
        absdist_x = abs(dist_x)
        absdist_y = abs(dist_y)
        dist = min(absdist_x, absdist_y) + abs(dist_x - dist_y) - 1
        c_hur = 0 # x, dist_y > dist_x
        if(absdist_x > absdist_y):
            c_hur = 1

        while(dist > 0):
            incr_x_mod = 1 if dist_x > 0 else 0 if dist_x == 0 else -1
            incr_y_mod = 1 if dist_y > 0 else 0 if dist_y == 0 else -1

            if(c_hur == 0 and dist_x * dist_y > 0):
                incr_x_mod = 0
            if(c_hur == 1 and dist_x * dist_y < 0):
                incr_y_mod = 0
            dist_x -= incr_x_mod
            dist_y -= incr_y_mod
            dest[0] += incr_x_mod
            dest[1] += incr_y_mod
            dist -= 1

            self.grid[self.to_local_coord(dest)].block = i
    
    def partial_reset(self):
        for i in range(self.dim[0] * self.dim[1]):
            self.grid[i].cost = maxsize
            self.grid[i].visited = False
            self.grid[i].from_node = [-1, -1]

    def construct(self, geo_size: int, geo_data: list[list[list[int]]]) -> None:
        self.grid = [Node(maxsize, -9) for i in range((self.dim[0] * self.dim[1] + 1))]
        for i in range(geo_size):
            i_geo_data = geo_data[i]
            tpos = i_geo_data[0]
            
            for pos in i_geo_data[1:]:
                #placing the starting anchor
                anchor = self.grid[self.to_local_coord(tpos)]
                anchor.anchor = True
                anchor.block = i
                dist_x = pos[0] - tpos[0]
                dist_y = pos[1] - tpos[1]
                
                dest = tpos.copy()
                self.line(i, dist_x, dist_y, dest)
                tpos = pos