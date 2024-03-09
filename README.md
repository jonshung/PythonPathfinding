# Python Pathfinding demonstration
![image](https://github.com/jonshung/PythonPathfinding/assets/110903974/5d6e4793-3dba-4f72-bf3d-f94b69c371c8)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<br>
<br>
This repository contains a simple demonstration of various different pathfinding algorithms on a 2D grid, all visualized on matplotlib's 3D engine.
# Prerequisites
```
- Python version >= 3.10
- Matplotlib version >= 2.1
```
# Usage
## Input format
The general input data format is a text file, whose content is defined as follow:
-  The first line contain the size of the 2D grid, separated by comma.
> An optional 3rd value can be used to define the visualization height.
- The second line contain the starting coordinate, the ending coordinate, and optional checkpoints which the result path must go through before reaching the end, all separated by commas.
- The third line contains an integer, be the number of shapes to be drawn on the graph. Each subsequent line contains the "anchor" points of each shape, which are then connected clockwisely such that the inner area of the shape is maximum.
- Shapes are set of points in which the algorithm can't move to or through.
Example:
```text
22,18,6
2,2,19,16,18,8,8,11
3
4,4,5,9,8,10,9,5
8,12,8,17,13,12
11,1,11,6,14,6,14,1 
```
<br>

## Retrieving input data and initializing the graph
Input are then retrieved into the program by creating an `InputData` object from the `input` module.
This data can be used to plug into any subsequent algorithm call.
A `Graph` object (of class Graph in the "graph" module) contains information of each nodes of the graph, as well as the original anchors of each shape.
It takes in a 2d list containing the x and y dimensions of the graph, as well as a list containing the anchors of each shape.

```python
dat = input.init_data("input.txt")
gg = graph.Graph(dat.dim, dat.geo_data) 
```

<br>
<br>

The graph object contains the `grid` property, which is a 1 dimension array containing m * n Node elements, for m and n is the dimension of the graph.
With any arbitrary x and y, we can use the function `graph.to_local_coord([x, y])` to translate from 2d coordinate to 1d coordinate of the `grid` list.
Each run of any algorithm might modify data fields in the graph's node, such as visited property, cost property, from_node, ... It is essential to reset the graph without having to draw the shapes again.
The `graph.partial_reset()` function iterate through all nodes in the graph, and set such properties to their default value.

## Showing the graph
After performing the necessary steps, we then can show the results using the visualize module.
For immediate and one-time run, we can use `visualize.show_graph` to avoid overhead.

```python
(function) def show_graph(
    grid: Graph,
    input_data: InputData,
    time: float = 0,
    show_expansion: bool = False,
    node_scale: float = 0.95
) -> None
```
<br>
The visualize module also allows the use of matplotlib's animation module, this can be used to visualize the algorithm execution through time, and is useful for cases where we want to change the graph and perform algorithm for each frame generated.

```python
(function) def updatable(
    graph_list: list[Graph],
    input_list: list[InputData],
    callback: Any,
    init_time: float = 0,
    interval: int = 1000,
    show_expansion: bool = False
) -> None
```
The `graph_list` and `input_list` property contains a list of graph to be iterated through and shown in each frame.

The callback function takes the signature:
```python
    (function) def callback(
    graph: Graph,
    input_data: InputData
) -> float
```
which returns a float, containing the time of execution of an algorithm in the callback's body; it can be defaulted to 0.

`graph` and `input_data` is the next graph in a list of graphs to be shown based on the current frame.
`init_time` can be used to show the time of the first algorithm run before callback.

## Additional features
For checkpoints, we can compute a route starting from the starting position, and ends in the ending position. This path must go through all checkpoints in any order such that the route has minimum cost.
This can be interpreted as an Open TSP problem.
The algorithm used to solve this is located in the `tsp.tsp` module, which utilize Dijkstra algorithm and Held-Karp algorithm to construct a pseudo graph, in which the vertices are the points to go through, and edges are path from each node to every other nodes.
<br>
In a graph, the method `graph.dynamic_geo`:

```python
(method) def dynamic_geo(
    self: Graph,
    direction: Any,
    h: Any
) -> None
```
can be used to move all shapes in one direction of h distance, `direction` can range from 0 -> 3, with 0 means moving all shapes in positive y axis, 1 moves shapes in positive x axis, 2 move shapes in negative y axis and 3 move shapes in negative x axis.
