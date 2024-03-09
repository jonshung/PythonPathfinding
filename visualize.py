import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from graph import Graph
from input import InputData
import numpy as np
from functools import partial

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

def explode(data):
    size = np.array(data.shape)*2
    data_e = np.zeros(size - 1, dtype=data.dtype)
    data_e[::2, ::2, ::2] = data
    return data_e

def rgbtostring(rgba: list):
    if(len(rgba) < 4):
        rgba.append(255)
    return '#%02x%02x%02x%02x' % (abs(rgba[0]), abs(rgba[1]), abs(rgba[2]), abs(rgba[3]))

def plot_voxel(voxels, colors, labels, scale):
    x, y, z = np.indices(np.array(voxels.shape) + 1).astype(float) // 2
    q = 1 - scale
    x[0::2, :, :] += q
    y[:, 0::2, :] += q
    z[:, :, 0::2] += q
    x[1::2, :, :] += scale
    y[:, 1::2, :] += scale
    z[:, :, 1::2] += scale
    
    ret = ax.voxels(x, y, z, voxels, facecolors=colors, edgecolors="k", shade=False)
    ax.legend(labels=labels)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')
    return ret

def build_voxel_map(grid: Graph, checkpoints: list[list[int]], show_expansion=False) -> list:
    dim = grid.dim.copy()

    z = 1 if len(dim) < 3 else dim[2]
    vox_grid = np.zeros((dim[0], dim[1], z))
    colors = np.ndarray((dim[0], dim[1], z), dtype=object)
    rstr = [['white']] * len(grid.geo_data)
    for i in range(len(grid.geo_data)):
        r = list(np.random.choice(range(127), size=3))
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

    if(checkpoints[-1] != None and len(checkpoints[-1]) >= 2):
        traceback = checkpoints[-1]
        max_z = grid.grid[grid.to_local_coord(traceback)].cost
        while(grid.in_boundary(traceback) and max_z > 0):
            vox_grid[traceback[0], traceback[1], 0] = False    # undo underlying node of path, saving compute resource

            n_node = grid.grid[grid.to_local_coord(traceback)]
            d_z = ramp_vl(n_node.cost, max_z, z)
            vox_grid[traceback[0], traceback[1], 0:(d_z + 1)] = True

            colors[traceback[0], traceback[1], 0:(d_z + 1)] = rgbtostring(lerp_color(n_node.cost / max_z, [0, 0, 255, 255], [255, 0, 0, 255]))
            traceback = n_node.from_node
    
    # recolor checkpoints
    for checkpoint in checkpoints:
        if(checkpoint == checkpoints[0] or checkpoint == checkpoints[-1]):
            c_col = rgbtostring([255, 0, 255])
        else:
            c_col = rgbtostring([0, 255, 0])
        vox_grid[checkpoint[0], checkpoint[1], 0:z] = True
        colors[checkpoint[0], checkpoint[1], 0:z] = c_col

    ex_voxels = explode(vox_grid)
    ex_colors = explode(colors)
    return [ex_voxels, ex_colors]

def lerp_color(x, col1: list, col2: list):
    f0 = (col2[0] - col1[0])
    f1 = (col2[1] - col1[1])
    f2 = (col2[2] - col1[2])
    if(len(col1) < 3):
        col1[3] = 255
    if(len(col2) < 3):
        col2[3] = 255
    f3 = col2[3] - col1[3]
    return [round(x * f0 + col1[0]), round(x * f1 + col1[1]), round(x * f2 + col1[2]), round(x * f3 + col1[3])]

def ramp_vl(x, max_x, ramps) -> int:
    return round((x / max_x) * ramps)

def show_graph(grid: Graph, input_data: InputData, time=0.0, show_expansion=False, node_scale=0.95):
    checkpoints = [input_data.start]
    for x in input_data.pickup:
        checkpoints.append(x)
    checkpoints.append(input_data.end)

    plot_data = build_voxel_map(grid, checkpoints, show_expansion)
    labels = [''] * 5
    labels[0] = "size=[%d, %d]" % (grid.dim[0] - 1, grid.dim[1] - 1)
    labels[1] = "start=%s" % (checkpoints[0])
    labels[2] = "end=%s" % (checkpoints[-1])
    labels[3] = "cost=%.2f" % (grid.grid[grid.to_local_coord(checkpoints[-1])].cost)
    labels[4] = "time=%.2fms" % (time * 1000)
    plot_voxel(plot_data[0], plot_data[1], labels, node_scale)
    plt.show()

def update(frame, graph_list: list[Graph], input_list: list[InputData], callback, time = [], show_expansion=False):
    i = frame % len(graph_list)
    grid = graph_list[i]
    input_data = input_list[i]
    
    checkpoints = [input_data.start]
    for x in input_data.pickup:
        checkpoints.append(x)
    checkpoints.append(input_data.end)

    voxel_map = build_voxel_map(graph_list[i], checkpoints, show_expansion=show_expansion)
    labels = [''] * 5
    labels[0] = "size=[%d, %d]" % (input_data.dim[0], input_data.dim[1])
    labels[1] = "start=%s" % (checkpoints[0])
    labels[2] = "end=%s" % (checkpoints[-1])
    labels[3] = "cost=%.2f" % (grid.grid[grid.to_local_coord(checkpoints[-1])].cost)
    if(len(time) == 0):
        time.append(0.0)
    labels[4] = "time=%.2fms" % (time[0] * 1000)
    ax.clear()

    time_ret = callback(graph_list[i], input_data)
    if(time_ret != None):
        time[0] = time_ret
    return plot_voxel(voxel_map[0], voxel_map[1], labels, 0.95)

def updatable(graph_list: list, input_list: list[InputData], callback, init_time=0.0, interval=1000, show_expansion=False):
    timer = [init_time]
    ani = FuncAnimation(fig, partial(update, graph_list=graph_list, input_list=input_list, callback=callback, \
                                    time=timer, show_expansion=show_expansion), interval=interval, cache_frame_data=False)
    plt.show()