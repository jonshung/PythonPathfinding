import input
import graph
import visualize
import algorithm
import gc

if __name__ == "__main__":
    dat = input.init_data("input.txt")
    gg = graph.Graph(dat.dim, dat.geo_size, dat.geo_data)
    algorithm.Astar(dat, gg)
    gc.collect()
    visualize.visualize_3d_graph(gg, dat.start, dat.end)