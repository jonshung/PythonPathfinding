import input
import graph
import visualize
import algorithm
import gc
import time

if __name__ == "__main__":
    dat = input.init_data("input.txt")
    gg = graph.Graph(dat.dim, dat.geo_data) 
    start_time = time.time()
    algorithm.Astar(dat, gg)
    end_time = time.time()
    # visualize.show_graph(gg, dat, end_time - start_time, True)
    
    # """
    def dynamic_geo_updater(graph: graph.Graph, input_data: input.InputData) -> float:
        graph.partial_reset()
        graph.dynamic_geo(1, 1)
        start_time = time.time()
        algorithm.Astar(input_data, graph)
        end_time = time.time()
        return end_time - start_time

    visualize.updatable([gg], [dat], dynamic_geo_updater, end_time - start_time, 1000, True)
    # """
