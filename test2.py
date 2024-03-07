import graph
import input
import tsp
import time
import visualize

if __name__ == "__main__":
    dat = input.init_data("input.txt")
    gg = graph.Graph(dat.dim, dat.geo_data)
    
    start_time = time.time()
    tsp.run(dat, gg)
    end_time = time.time()
    visualize.show_graph(gg, dat, end_time - start_time, True)