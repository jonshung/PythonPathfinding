import re

class InputData:
    dim: list[int]
    start: list[int]
    end: list[int]
    pickup: list[list[int]]
    geo_size: int
    geo_data: list[list[list[int]]]
    
    def __init__(self, dim_v: list[int], start_v: list[int], end_v: list[int], \
                 pickup_v: list[list[int]], geo_size_v: int, geo_data_v: list[list[list[int]]]) -> None:
        self.dim = dim_v
        self.start = start_v
        self.end = end_v
        self.pickup = pickup_v
        self.geo_size = geo_size_v
        self.geo_data = geo_data_v

def sanitize_pair(inp: str) -> list:
    pair =  [int(x) for x in re.findall(r'[^,.]+', inp)]
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

    return InputData(dim, start, end, pickup, geo_size, geo_data)