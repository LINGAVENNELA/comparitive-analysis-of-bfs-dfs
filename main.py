import os
import time
from grid_config import grid, start, goal
from bfs import bfs
from dfs import dfs

os.makedirs("results", exist_ok=True)

print("Select Mode: \n1. BFS\n2. DFS\n3. GUI Visualization")
choice = input("Enter choice: ")
if choice == "1":
    start_time = time.time()
    path, nodes = bfs(grid, start, goal)
    exec_time = time.time() - start_time
    print(f"BFS Path: {path}")
    print(f"Length: {len(path)} | Time: {exec_time:.4f}s | Nodes Visited: {nodes}")

elif choice == "2":
    start_time = time.time()
    path, nodes = dfs(grid, start, goal)
    exec_time = time.time() - start_time
    print(f"DFS Path: {path}")
    print(f"Length: {len(path)} | Time: {exec_time:.4f}s | Nodes Visited: {nodes}")

