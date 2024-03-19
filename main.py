import pathfinding
import algorithm
import tsp

if __name__ == "__main__":
    pathfinding.run_multi("input.txt", algorithm.Astar, 1000)