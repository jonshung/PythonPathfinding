from sys import maxsize

class Node:
    block: int = -9 # 0 -> +inf: geometry, -1: node expanded, -2: path, -9: open node, 
                    # -10: visited but not expanded i.e not popped, <= -11: geometry on previous path
    anchor: bool = False
    cost: float = maxsize       # depends on the algorithm, for BestFirsts', it is the PATH-COST, i.e cost from start -> current node
    visited = False             # trivial property for reached state 
    from_node = [-1, -1]        # coordinate of parent node

    def __repr__(self) -> str:
        return str(self.block)

    def __init__(self, cost_vl, block_vl) -> None:
        self.cost = cost_vl
        self.block = block_vl

move_direction = [[0, 1], [1, 0], [0, -1], [-1, 0], [1, 1], [-1, 1], [-1, -1], [1, -1]]
class Graph:
    grid: list[Node]            # a M x N, 1D array containing informations of each node
    dim: list[int]              # dimension, dim[0] = x, dim[1] = y
    geo_data: list

    def __repr__(self) -> str:
        stri = ""
        n = self.dim[0] + 1
        for i in range(0, len(self.grid), n):
            stri += str(self.grid[i:i+n])
            stri += "\n"
        return stri

    def __init__(self, dim_vl: list[int], geo_data_vl: list[list[list[int]]]) -> None:
        self.dim = dim_vl
        self.dim[0] += 1
        self.dim[1] += 1
        for i in range(len(self.dim)):
            if self.dim[i] <= 0:
                self.dim[i] = 1
        self.geo_data = geo_data_vl
        self.construct(len(geo_data_vl), geo_data_vl)

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
        return  self._in_boundary(x, y)  and self.grid[local].block <= -9 and self.grid[local].block > -11
    
    def can_move_straight(self, pos: list[int]) -> bool:
        if(len(pos) < 2):
            return False
        return self._can_move_straight(x=pos[0], y=pos[1])
    
    def _can_move_diagonal(self, from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        if(self._in_boundary(to_x, to_y) == False):
            return False
        #check going through wall
        unblocked = (self.grid[self._to_local_coord(to_x, to_y)].block <= -9 and self.grid[self._to_local_coord(to_x, to_y)].block > -11) and \
                    ((self.grid[self._to_local_coord(from_x, to_y)].block <= -9 and self.grid[self._to_local_coord(from_x, to_y)].block > -11) or \
                    (self.grid[self._to_local_coord(to_x, from_y)].block <= -9 and self.grid[self._to_local_coord(to_x, from_y)].block > -11))
        return unblocked
    
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
    
    def partial_reset(self, reset_path=True):
        for i in range(self.dim[0] * self.dim[1]):
            if(self.grid[i].block >= 0 or (not reset_path and self.grid[i].block <= -11) or (not reset_path and self.grid[i].block == -2)):
                continue
            self.grid[i].cost = maxsize
            self.grid[i].visited = False
            self.grid[i].from_node = [-1, -1]
            if(self.grid[i].block <= -11):
                self.grid[i].block = -11 - self.grid[i].block
            else:
                self.grid[i].block = -9

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

    def symmetrical_translation(self, x2, y2):
        x_translation = int(x2)
        y_translation = int(y2)
        changed = False
        if(x2 >= (self.dim[0] - 1)):
            x_translation = x2 - self.dim[0] + 2
            changed = True
        if(x2 <= 0):
            x_translation = self.dim[0] - 2 + x2
            changed = True
        if(y2 >= (self.dim[1] - 1)):
            y_translation = y2 - self.dim[1] + 2
            changed = True
        if(y2 <= 0):
            y_translation = self.dim[1] - 2 + y2
            changed = True
        return (self.symmetrical_translation(x_translation, y_translation)) if changed else [x_translation, y_translation]

    # direction 0: up, 1: right, 2: down, 3: left, 4 = upper right, 5 = upper left,
    # 6 = lower left, 7 = lower right
    def dynamic_geo(self, direction, h):
        if(direction < 0 or direction > 7):
            return
        move_vector = move_direction[direction]
        t_grid = [Node(maxsize, -9) for i in range((self.dim[0] * self.dim[1] + 1))]
        for i in range(1, self.dim[0]):
            for j in range(1, self.dim[1]):
                node = self.grid[self._to_local_coord(i, j)]

                if(node.block >= 0 or node.block <= -11):
                    d_x = move_vector[0] * h + i
                    d_y = move_vector[1] * h + j
                    translation = self.symmetrical_translation(d_x, d_y)
                    if(self.grid[self.to_local_coord(translation)].block == -2 or self.grid[self.to_local_coord(translation)].block <= -11):
                        block = node.block
                        if(node.block <= -11):
                            block = -11 - node.block
                        
                        t_grid[self.to_local_coord(translation)].block = -11 - block
                        t_grid[self.to_local_coord(translation)].cost = self.grid[self.to_local_coord(translation)].cost
                        t_grid[self.to_local_coord(translation)].visited = self.grid[self.to_local_coord(translation)].visited
                        t_grid[self.to_local_coord(translation)].from_node = self.grid[self.to_local_coord(translation)].from_node
                    else:
                        block = node.block
                        if(node.block <= -11):
                            block = -11 - node.block
                        t_grid[self.to_local_coord(translation)].block = block
                    if(node.block <= -11):
                        t_grid[self._to_local_coord(i, j)].block = -2
                        t_grid[self._to_local_coord(i, j)].cost = node.cost
                        t_grid[self._to_local_coord(i, j)].visited = node.visited
                        t_grid[self._to_local_coord(i, j)].from_node = node.from_node

                elif(node.block == -2):
                    cost = node.cost
                    t_grid[self._to_local_coord(i, j)].block = -2
                    t_grid[self._to_local_coord(i, j)].cost = cost
                    t_grid[self._to_local_coord(i, j)].visited = node.visited
                    t_grid[self._to_local_coord(i, j)].from_node = node.from_node

        self.grid = t_grid