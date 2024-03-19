from vispy import app, scene
from vispy.color import Color
from vispy.scene.visuals import Text
import numpy as np
from graph import Graph
from input import InputData
from multi_cube import MultiCube, MultiCubeVisual
from visualize_helper import lerp_color, ramp_vl
import threading
import functools
from sys import maxsize

canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), bgcolor='w')
view = canvas.central_widget.add_view()

camera = scene.cameras.ArcballCamera(parent=view.scene, fov=40)
view.camera = camera

def get_color_array(c, alpha, size, cmap="viridis"):
    if c is not None:
        if hasattr(c, "__iter__"):
            c = np.array(c, copy=True, dtype=float)
            c -= c.min() 
            c *= 255/c.max()
    else:
        color = np.ones((size, 4))
        color[:, 3] = alpha
        return color

cubes: MultiCubeVisual = None
def plot_grid_cubes(mergedData, c=None, size=1, edge_color="black", alpha=1, cmap="viridis"):
    global cubes
    
    if(cubes == None):
        cubes = MultiCube(size, positions=mergedData, edge_color=edge_color, face_colors=c)
        view.add(cubes)
    else:
        drawthread.job = functools.partial(cubes.set_data, size=size, positions=mergedData, edge_color=edge_color, face_colors=c)
        thread = threading.Thread(target = drawthread.exec)
        thread.start()

def plot_voxel(voxels: np.ndarray, colors: np.ndarray, size=1):
    xyz = voxels.nonzero()
    mergedData = np.vstack((xyz[0], xyz[1], xyz[2])).T
    col_1d = np.ndarray(len(xyz[0]), dtype=Color)
    for i in range(len(xyz[0])):
        x = xyz[0][i]
        y = xyz[1][i]
        z = xyz[2][i]
        col_1d[i] = Color(colors[x, y, z])
    plot_grid_cubes(mergedData=mergedData, c=col_1d, size=size)
    
def rgbtostring(rgba: list):
    if(len(rgba) < 4):
        rgba.append(255)
    return '#%02x%02x%02x%02x' % (abs(rgba[0]), abs(rgba[1]), abs(rgba[2]), abs(rgba[3]))

def build_voxel_map(grid: Graph, checkpoints: list[list[int]], show_expansion=False, found = False) -> list:
    dim = grid.dim.copy()

    z = 2 if len(dim) < 3 else (dim[2] + 1)
    vox_grid = np.zeros((dim[0], dim[1], z))
    colors = np.ndarray((dim[0], dim[1], z), dtype=object)
    rstr = [['white']] * len(grid.geo_data)
    for i in range(len(grid.geo_data)):
        r = list(np.random.choice(range(127), size=3))
        rstr[i] = rgbtostring(r)
    colors[:, :, :] = rgbtostring([255, 255, 255, 127]) # white
    
    max_z = grid.grid[grid.to_local_coord(checkpoints[-1])].cost if found else maxsize
    for y in range(dim[1]):
        for x in range(dim[0]):
            idx = grid._to_local_coord(x, y)
            vox_grid[x, y, 0] = True
            # grid basic
            if(x == 0 or x == (dim[0] - 1) or y == 0 or y == (dim[1] - 1)):
                colors[x, y, 0] = rgbtostring([178, 178, 178]) # gray
            elif(grid.grid[idx].block >= 0):
                vox_grid[x, y, 1:int(z/2)] = True
                colors[x, y, :int(z/2)] = rstr[grid.grid[idx].block]
            elif(grid.grid[idx].block <= -11 and not found):
                vox_grid[x, y, 1:int(z/2)] = True
                colors[x, y, :int(z/2)] = rstr[-11 - grid.grid[idx].block]
                # todo: only anchor should have darker anchors
                # interconnecting nodes between anchor should be lighter

            # algorithm data
            elif(grid.grid[idx].visited and show_expansion):
                if(grid.grid[idx].block == -10):   # unexpanded frontier
                    colors[x, y, 0] = rgbtostring([0, 255, 0, 127])
                elif(grid.grid[idx].block == -1):  # expanded
                    colors[x, y, 0] = rgbtostring([255, 0, 0, 127])
                elif(grid.grid[idx].block == -2 or (grid.grid[idx].block <= -11 and found)): # path
                    vox_grid[x, y, 0] = False    # undo underlying node of path, saving compute resource
                    n_node = grid.grid[grid.to_local_coord([x, y])]
                    d_z = ramp_vl(n_node.cost, max_z, z)
                    vox_grid[x, y, 1:(d_z + 2)] = True

                    colors[x, y, 1:(d_z + 2)] = rgbtostring(lerp_color(min(1, n_node.cost / max_z), [0, 0, 255, 255], [255, 0, 0, 255]))
    
    # recolor checkpoints
    for checkpoint in checkpoints:
        if(checkpoint == checkpoints[0] or checkpoint == checkpoints[-1]):
            c_col = rgbtostring([255, 0, 255])
        else:
            c_col = rgbtostring([0, 255, 0])
        vox_grid[checkpoint[0], checkpoint[1], 0:z] = True
        colors[checkpoint[0], checkpoint[1], 0:z] = c_col
    return [vox_grid, colors]

def show_graph(graph: Graph, input_data: InputData, time=0.0, show_expansion=False, size=1):
    checkpoints = [input_data.start]
    for x in input_data.pickup:
        checkpoints.append(x)
    checkpoints.append(input_data.end)

    plot_data = build_voxel_map(graph, checkpoints, show_expansion, input_data.found)
    plot_voxel(plot_data[0], plot_data[1], size=size)
    build_label(graph, input_data, time)
    canvas.show()
    app.run()

def update(event):
    if((global_graph is None) or (global_input_data is None) or (global_callback is None) or (drawthread.run_next == False)):
        return
    prev = global_input_data.found
    time_ret = global_callback(global_graph, global_input_data)
    if(global_input_data.found and prev):
        return 0
    checkpoints = [global_input_data.start]
    for x in global_input_data.pickup:
        checkpoints.append(x)
    checkpoints.append(global_input_data.end)
    voxel_map = build_voxel_map(global_graph, checkpoints, global_show_expansion, global_input_data.found)
    build_label(global_graph, global_input_data, time_ret)
    return plot_voxel(voxel_map[0], voxel_map[1], global_size)

def build_label(graph: Graph, input_data: InputData, time = 0.0):
    global labels
    if labels is None:
        labels = [Text(parent=canvas.scene, color="black", font_size=12) for i in range(5)]
        for i in range(len(labels)):
            labels[i].pos = 70, 50 + 50 * i
    labels[0].text = "size=[%d, %d]" % (graph.dim[0] - 1, graph.dim[1] - 1)
    labels[1].text = "start=%s" % (input_data.start)
    labels[2].text = "end=%s" % (input_data.end)
    labels[3].text = "cost=%.2f" % (graph.grid[graph.to_local_coord(input_data.end)].cost)
    if(time >= 0):
        labels[4].text = "time=%.2fms" % (time * 1000)
    for i in range(5):
        labels[i].update()
labels = None

class DrawThread:
    def __init__(self, job=None, run=True):
        self.job = job
        self.run = run
        self.run_next = True

    def exec(self):
        if self.job is not None:
            self.run_next = False
            self.job()
            self.run_next = True


def updatable(grid: Graph, input_data: InputData, callback, init_time=0.0, interval=1000, show_expansion=False, size=1):
    global global_graph
    global global_input_data
    global global_callback
    global global_show_expansion
    global drawthread
    global global_size

    global_graph = grid
    global_input_data = input_data
    global_show_expansion = show_expansion
    global_size = size
    global_callback = callback
    drawthread = DrawThread()

    timer = app.Timer()
    timer.connect(update)
    timer.start(interval / 1000, -1)  # interval, iterations
    show_graph(grid, input_data, init_time, show_expansion, size)