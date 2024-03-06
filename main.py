import input
import graph
import visualize
import algorithm
import gc

if __name__ == "__main__":
    dat = input.init_data("input.txt")
    gg = graph.Graph(dat.dim, dat.geo_data) 
    #algorithm.Astar(dat, gg)

    gc.collect()
    #visualize.visualize_3d_graph(gg, [dat.start, dat.end])

    dat1 = input.init_data("input.txt")
    gg1 = graph.Graph(dat1.dim, dat1.geo_data)

    def dynamic_geo_updater(graph_list: list[graph.Graph], dat: list):
        for g in graph_list:
            g.partial_reset()
            g.dynamic_geo(2, 1)
            algorithm.Astar(dat1, gg1)
    visualize.updatable([gg1], [dat1], dynamic_geo_updater, 1000)
