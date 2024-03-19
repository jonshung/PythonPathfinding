import re

class InputData:
    dim: list[int]
    start: list[int]
    org_start: list[int]
    end: list[int]
    pickup: list[list[int]]
    geo_size: int
    geo_data: list[list[list[int]]]
    move_speed = 0
    geo_directon = -1
    geo_h = 0
    hold_frame = -1
    
    def __init__(self, dim_v: list[int], start_v: list[int], end_v: list[int], \
                 pickup_v: list[list[int]], geo_size_v: int, geo_data_v: list[list[list[int]]], move_speed: int | None,
                   geo_directon: int | None, geo_h: int | None, hold_frame: int | None) -> None:
        self.dim = dim_v
        self.start = start_v
        self.org_start = start_v
        self.end = end_v
        self.pickup = pickup_v
        self.geo_size = geo_size_v
        self.geo_data = geo_data_v
        self.move_speed = move_speed
        self.geo_directon = geo_directon
        self.geo_h = geo_h
        self.hold_frame = hold_frame
        self.frame = 0
        self.found = False

def sanitize_pair(inp: str) -> list:
    pair = [int(x) for x in re.findall(r'[^,.]+', inp)]
    return pair

def init_data(filename: str):
    with open(filename) as f:
        dim = sanitize_pair(f.readline())
        pairs = [sanitize_pair(x) for x in re.findall(r'([0-9]+\s*[.,]+\s*[0-9]+)', f.readline())]
        start = pairs[0]
        end = pairs[1]
        pickup = pairs[2:]

        geo_size = int(f.readline())
        geo_data = [[[0, 0]]] * geo_size
        for i in range(geo_size):
            geo_data[i] = [sanitize_pair(str(x)) for x in re.findall(r'([0-9]+\s*[.,]+\s*[0-9]+)', f.readline())]
            if(len(geo_data[i]) > 0):
                geo_data[i].append(geo_data[i][0].copy())
        move_data = f.readline().split(',')
        for x in range(len(move_data)):
            try:
                dec = int(move_data[x])
                move_data[x] = dec
            except ValueError:
                move_data = []
                break
        move_speed = 0
        dir = -1
        h = 0
        hold_frame = -1
        if(len(move_data) >= 3):
            move_speed = move_data[0]
            dir = move_data[1]
            h = move_data[2]
            if(len(move_data) >= 4):
                hold_frame = move_data[3]

    return InputData(dim, start, end, pickup, geo_size, geo_data, move_speed, dir, h, hold_frame)