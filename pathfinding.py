import sys
import importlib.util
import input
import graph
import time
import algorithm

vispy = None
def import_mod(name):
    if (spec := importlib.util.find_spec(name)) is not None:
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    return -1

required = {'numpy'}
for module_name in required:
    if(module_name in sys.modules):
        continue
    elif (spec := importlib.util.find_spec(module_name)) is not None:
        import_mod(module_name)
    else:
        print(f"can't find the {module_name!r} module")

backend = import_mod('vispy')
if(backend == -1):
    backend = import_mod('matplotlib')
    if(backend == -1):
        raise RuntimeError("Error: no backend detected")
    else:
        backend = import_mod('visualize_matplot')
else:
    backend = import_mod('visualize_gpu')

def run(input_file):
    if(backend == -1):
        raise RuntimeError("Error: no backend detected")
    dat = input.init_data(input_file)
    gg = graph.Graph(dat.dim, dat.geo_data) 
    start_time = time.time()
    if(not algorithm.Astar(dat, gg)):
        gg.grid[gg.to_local_coord(dat.end)].cost = -1
    end_time = time.time()
    backend.show_graph(gg, dat, end_time - start_time, True)

def run_multi(input_file, interval = 1000):
    if(backend == -1):
        raise RuntimeError("Error: no backend detected")
    dat = input.init_data(input_file)
    gg = graph.Graph(dat.dim, dat.geo_data) 
    start_time = time.time()
    algorithm.Astar(dat, gg, dat.move_speed)
    end_time = time.time()

    def dynamic_geo_updater(graph: graph.Graph, input_data: input.InputData) -> float:
        if(input_data.found):
            input_data.frame += 1
            if(input_data.hold_frame >= 0 and input_data.frame >= input_data.hold_frame):
                input_data.found = False
                graph.partial_reset()
                input_data.frame = 0
                return dynamic_geo_updater(graph, input_data)
            else:
                return -1
        graph.partial_reset(False)
        graph.dynamic_geo(input_data.geo_directon, input_data.geo_h)
        start_time = time.time()
        input_data.found = algorithm.Astar(input_data, graph, dat.move_speed)
        if(input_data.found):
            input_data.start = input_data.org_start
        end_time = time.time()
        return end_time - start_time

    backend.updatable(gg, dat, dynamic_geo_updater, end_time - start_time, interval, True)