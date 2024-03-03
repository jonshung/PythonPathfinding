import matplotlib.pyplot as plt
import matplotlib.colors as colorplt
from graph import Graph
import numpy as np

def explode(data):
    size = np.array(data.shape)*2
    data_e = np.zeros(size - 1, dtype=data.dtype)
    data_e[::2, ::2, ::2] = data
    return data_e

def rgbtostring(rgba: list):
    if(len(rgba) < 4):
        rgba.append(255)
    return '#%02x%02x%02x%02x' % (rgba[0], rgba[1], rgba[2], rgba[3])

def visualize_3d_graph(grid: Graph, start: list, end: list, show_expansion=False, node_scale=0.95):
    dim = grid.dim.copy()
    fig = plt.figure()
    fig.tight_layout()
    ax = fig.add_subplot(projection='3d')
    fig.tight_layout()
    
    vox_grid = np.zeros((dim[0], dim[1], 2))
    colors = np.ndarray((dim[0], dim[1], 2), dtype=object)
    rstr = [['white']] * grid.geo_size
    for i in range(grid.geo_size):
        r = list(np.random.choice(range(256), size=3))
        #r.append(127)
        rstr[i] = rgbtostring(r)
    colors[:, :, :] = rgbtostring([255, 255, 255, 127]) # white

    for y in range(dim[1]):
        for x in range(dim[0]):
            idx = grid._to_local_coord(x, y)
            vox_grid[x, y, 0] = True
            # grid basic
            if(x == 0 or x == (dim[0] - 1) or y == 0 or y == (dim[1] - 1)):
                colors[x, y, 0] = rgbtostring([178, 178, 178]) # gray
            elif(grid.grid[idx].block >= 0):
                colors[x, y, 0] = rstr[grid.grid[idx].block]
                # todo: only anchor should have darker anchors
                # interconnecting nodes between anchor should be lighter

            # algorithm data
            elif(grid.grid[idx].visited and show_expansion):
                if(grid.grid[idx].block == -10):   # unexpanded frontier
                    colors[x, y, 0] = rgbtostring([0, 255, 0, 127])
                elif(grid.grid[idx].block == -1):  # expanded
                    colors[x, y, 0] = rgbtostring([255, 0, 0, 127])

    found = False
    if(end != None and len(end) >= 2):
        traceback = end
        # in case path not found, still display start, stop
        vox_grid[end[0], end[1], 1] = True
        vox_grid[start[0], start[1], 1] = True

        while(grid.in_boundary(traceback)):
            if(traceback[0] == start[0] and traceback[1] == start[1]):
                found = True
            
            vox_grid[traceback[0], traceback[1], 0] = False    # undo underlying node of path, saving compute resource
            vox_grid[traceback[0], traceback[1], 1] = True
            colors[traceback[0], traceback[1], 1] = rgbtostring([0, 0, 255, 255])
            n_node = grid.grid[grid.to_local_coord(traceback)]
            traceback = n_node.from_node
        
        # recolor start and end
        colors[end[0], end[1], 1] = rgbtostring([255, 0, 255])
        colors[start[0], start[1], 1] = rgbtostring([255, 0, 255])
    
    filled = explode(vox_grid)
    fcolors = explode(colors)

    # offsetting nodes
    x, y, z = np.indices(np.array(filled.shape) + 1).astype(float) // 2
    q = 1 - node_scale
    x[0::2, :, :] += q
    y[:, 0::2, :] += q
    z[:, :, 0::2] += q
    x[1::2, :, :] += node_scale
    y[:, 1::2, :] += node_scale
    z[:, :, 1::2] += node_scale
    
    ax.voxels(x, y, z, filled, facecolors=fcolors, edgecolors="k", shade=False)
    labels = [''] * 5
    labels[0] = "size=%s" % (grid.dim)
    labels[1] = "start=%s" % (start)
    labels[2] = "end=%s" % (end)
    labels[3] = "found=%s" % ("true" if found else "false")
    labels[4] = "cost=%d" % (grid.grid[grid.to_local_coord(end)].cost if found else -1)
    ax.legend(labels=labels)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')
    plt.show()