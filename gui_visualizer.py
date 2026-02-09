import tkinter as tk
from collections import deque
import time

CELL = 36         # pixels per cell
PADDING = 12      # spacing between BFS and DFS canvases

# --- Step generators: BFS and DFS, yield states for each step ---
def bfs_step(grid, start, goal):
    moves = [(1,0),(-1,0),(0,1),(0,-1)]
    q = deque([start])
    parent = {start: None}
    visited = set()
    nodes_visited = 0
    max_space = 1

    while q:
        node = q.popleft()
        nodes_visited += 1
        visited.add(node)
        max_space = max(max_space, len(q)+1)
        # yield a visit event
        yield ("visit", node, list(q), visited.copy(), nodes_visited, max_space)

        if node == goal:
            # reconstruct path
            path = []
            n = node
            while n is not None:
                path.append(n)
                n = parent[n]
            yield ("done", path[::-1], nodes_visited, max_space)
            return

        for dx, dy in moves:
            x, y = node[0] + dx, node[1] + dy
            if 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] == 0:
                if (x, y) not in parent:
                    parent[(x, y)] = node
                    q.append((x, y))

    yield ("failed", [], nodes_visited, max_space)


def dfs_step(grid, start, goal):
    moves = [(1,0),(-1,0),(0,1),(0,-1)]
    stack = [start]
    parent = {start: None}
    visited = set()
    nodes_visited = 0
    max_space = 1

    while stack:
        node = stack.pop()
        nodes_visited += 1
        visited.add(node)
        max_space = max(max_space, len(stack)+1)
        yield ("visit", node, list(stack), visited.copy(), nodes_visited, max_space)

        if node == goal:
            path = []
            n = node
            while n is not None:
                path.append(n)
                n = parent[n]
            yield ("done", path[::-1], nodes_visited, max_space)
            return

        for dx, dy in moves:
            x, y = node[0] + dx, node[1] + dy
            if 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] == 0:
                if (x, y) not in parent:
                    parent[(x, y)] = node
                    stack.append((x, y))

    yield ("failed", [], nodes_visited, max_space)


# --- GUI ---
def run_gui(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    # Window
    root = tk.Tk()
    root.title("Comparative BFS vs DFS — Step-by-step (2D graph)")

    # Top frame: canvases + stats
    top = tk.Frame(root)
    top.pack(padx=8, pady=8)

    # Canvas width and height
    cw = cols * CELL
    ch = rows * CELL

    # BFS canvas (left)
    canvas_bfs = tk.Canvas(top, width=cw, height=ch, bg="white")
    canvas_bfs.grid(row=0, column=0)
    # little label
    tk.Label(top, text="BFS (left)", font=("Arial", 10, "bold")).grid(row=1, column=0, pady=(4,0))

    # DFS canvas (right)
    canvas_dfs = tk.Canvas(top, width=cw, height=ch, bg="white")
    canvas_dfs.grid(row=0, column=2, padx=(PADDING,0))
    tk.Label(top, text="DFS (right)", font=("Arial", 10, "bold")).grid(row=1, column=2, pady=(4,0))

    # Stats panel between canvases
    stats_frame = tk.Frame(top)
    stats_frame.grid(row=0, column=1, padx=(8,8))
    tk.Label(stats_frame, text="Live Statistics", font=("Arial", 11, "bold")).pack(pady=(2,6))
    bfs_stats = tk.Label(stats_frame, text="BFS:\nNodes visited: 0\nMax queue: 0\nPath length: -\nTime: -", justify="left")
    bfs_stats.pack(pady=4)
    dfs_stats = tk.Label(stats_frame, text="DFS:\nNodes visited: 0\nMax stack: 0\nPath length: -\nTime: -", justify="left")
    dfs_stats.pack(pady=4)

    # Control frame
    ctrl = tk.Frame(root)
    ctrl.pack(pady=8)

    # Buttons + Speed
    btn_next = tk.Button(ctrl, text="Next Step")
    btn_run = tk.Button(ctrl, text="Run")
    btn_pause = tk.Button(ctrl, text="Pause")
    btn_reset = tk.Button(ctrl, text="Reset")
    speed_label = tk.Label(ctrl, text="Speed (ms):")
    speed_scale = tk.Scale(ctrl, from_=50, to=1000, orient="horizontal")
    speed_scale.set(250)

    btn_next.grid(row=0, column=0, padx=6)
    btn_run.grid(row=0, column=1, padx=6)
    btn_pause.grid(row=0, column=2, padx=6)
    btn_reset.grid(row=0, column=3, padx=6)
    speed_label.grid(row=0, column=4, padx=(12,2))
    speed_scale.grid(row=0, column=5)

    # Drawing grids (cells -> rectangles) for both canvases
    bfs_cells = [[None for _ in range(cols)] for __ in range(rows)]
    dfs_cells = [[None for _ in range(cols)] for __ in range(rows)]

    def draw_initial():
        for i in range(rows):
            for j in range(cols):
                x1 = j*CELL; y1 = i*CELL; x2 = x1+CELL; y2 = y1+CELL
                color = "black" if grid[i][j]==1 else "white"
                bfs_cells[i][j] = canvas_bfs.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
                dfs_cells[i][j] = canvas_dfs.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
        # start and goal
        sx, sy = start; gx, gy = goal
        canvas_bfs.itemconfig(bfs_cells[sx][sy], fill="green")
        canvas_bfs.itemconfig(bfs_cells[gx][gy], fill="red")
        canvas_dfs.itemconfig(dfs_cells[sx][sy], fill="green")
        canvas_dfs.itemconfig(dfs_cells[gx][gy], fill="red")

    draw_initial()

    # Generators
    bfs_gen = bfs_step(grid, start, goal)
    dfs_gen = dfs_step(grid, start, goal)

    # State flags
    running = {"value": False}
    bfs_done = {"value": False}
    dfs_done = {"value": False}
    bfs_info = {"nodes":0, "max_space":0, "path":[] , "time":None}
    dfs_info = {"nodes":0, "max_space":0, "path":[] , "time":None}

    # Helper to color a visited node (but don't overwrite start/goal)
    def color_cell(canvas, cell_rects, i, j, color):
        # preserve start/goal colors:
        if (i,j) == start:
            canvas.itemconfig(cell_rects[i][j], fill="green")
        elif (i,j) == goal:
            canvas.itemconfig(cell_rects[i][j], fill="red")
        else:
            canvas.itemconfig(cell_rects[i][j], fill=color)

    # step function: advances both BFS and DFS one step
    def step_once():
        # BFS step
        try:
            ev = next(bfs_gen)
            if ev[0] == "visit":
                _, node, q_snapshot, visited_set, nodes_visited, max_space = ev
                bfs_info["nodes"] = nodes_visited
                bfs_info["max_space"] = max_space
                # color visited node blue, highlight as current yellow then blue
                i,j = node
                color_cell(canvas_bfs, bfs_cells, i, j, "yellow")
                # small delay to show current highlight:
                canvas_bfs.after(1, lambda: color_cell(canvas_bfs, bfs_cells, i, j, "blue"))
            elif ev[0] == "done":
                _, path, nodes_visited, max_space = ev
                bfs_info["path"] = path
                bfs_info["nodes"] = nodes_visited
                bfs_info["max_space"] = max_space
                bfs_info["time"] = bfs_info.get("start_time") and (time.time() - bfs_info["start_time"])
                bfs_done["value"] = True
                # highlight full path
                for (pi,pj) in path:
                    color_cell(canvas_bfs, bfs_cells, pi, pj, "gold")
            elif ev[0] == "failed":
                bfs_done["value"] = True
        except StopIteration:
            bfs_done["value"] = True

        # DFS step
        try:
            ev = next(dfs_gen)
            if ev[0] == "visit":
                _, node, stack_snapshot, visited_set, nodes_visited, max_space = ev
                dfs_info["nodes"] = nodes_visited
                dfs_info["max_space"] = max_space
                i,j = node
                color_cell(canvas_dfs, dfs_cells, i, j, "yellow")
                canvas_dfs.after(1, lambda: color_cell(canvas_dfs, dfs_cells, i, j, "orange"))
            elif ev[0] == "done":
                _, path, nodes_visited, max_space = ev
                dfs_info["path"] = path
                dfs_info["nodes"] = nodes_visited
                dfs_info["max_space"] = max_space
                dfs_info["time"] = dfs_info.get("start_time") and (time.time() - dfs_info["start_time"])
                dfs_done["value"] = True
                for (pi,pj) in path:
                    color_cell(canvas_dfs, dfs_cells, pi, pj, "gold")
            elif ev[0] == "failed":
                dfs_done["value"] = True
        except StopIteration:
            dfs_done["value"] = True

        update_stats_labels()

    # update stats display
    def update_stats_labels():
        bfs_path_len = len(bfs_info["path"]) if bfs_info["path"] else "-"
        dfs_path_len = len(dfs_info["path"]) if dfs_info["path"] else "-"
        bfs_time = f"{bfs_info['time']:.4f}s" if bfs_info.get("time") else ("running" if not bfs_done["value"] else "-")
        dfs_time = f"{dfs_info['time']:.4f}s" if dfs_info.get("time") else ("running" if not dfs_done["value"] else "-")
        bfs_stats.config(text=f"BFS:\nNodes visited: {bfs_info['nodes']}\nMax queue: {bfs_info['max_space']}\nPath length: {bfs_path_len}\nTime: {bfs_time}")
        dfs_stats.config(text=f"DFS:\nNodes visited: {dfs_info['nodes']}\nMax stack: {dfs_info['max_space']}\nPath length: {dfs_path_len}\nTime: {dfs_time}")

    # Run loop using after()
    def run_loop():
        if not running["value"]:
            return
        step_once()
        # stop if both done
        if bfs_done["value"] and dfs_done["value"]:
            running["value"] = False
            # finalize times if not set
            if bfs_info.get("start_time") and not bfs_info.get("time"):
                bfs_info["time"] = time.time() - bfs_info["start_time"]
            if dfs_info.get("start_time") and not dfs_info.get("time"):
                dfs_info["time"] = time.time() - dfs_info["start_time"]
            update_stats_labels()
            return
        delay = speed_scale.get()
        root.after(delay, run_loop)

    # Button callbacks
    def on_next():
        # ensure start_time set first time we step
        if not bfs_info.get("start_time"):
            bfs_info["start_time"] = time.time()
        if not dfs_info.get("start_time"):
            dfs_info["start_time"] = time.time()
        step_once()

    def on_run():
        if bfs_done["value"] and dfs_done["value"]:
            return
        running["value"] = True
        if not bfs_info.get("start_time"):
            bfs_info["start_time"] = time.time()
        if not dfs_info.get("start_time"):
            dfs_info["start_time"] = time.time()
        run_loop()

    def on_pause():
        running["value"] = False

    def on_reset():
        nonlocal bfs_gen, dfs_gen
        running["value"] = False
        bfs_done["value"] = False
        dfs_done["value"] = False
        bfs_info.update({"nodes":0,"max_space":0,"path":[],"time":None,"start_time":None})
        dfs_info.update({"nodes":0,"max_space":0,"path":[],"time":None,"start_time":None})
        bfs_gen = bfs_step(grid, start, goal)
        dfs_gen = dfs_step(grid, start, goal)
        # redraw initial canvas colors
        for i in range(rows):
            for j in range(cols):
                color = "black" if grid[i][j]==1 else "white"
                canvas_bfs.itemconfig(bfs_cells[i][j], fill=color)
                canvas_dfs.itemconfig(dfs_cells[i][j], fill=color)
        sx, sy = start; gx, gy = goal
        canvas_bfs.itemconfig(bfs_cells[sx][sy], fill="green")
        canvas_bfs.itemconfig(bfs_cells[gx][gy], fill="red")
        canvas_dfs.itemconfig(dfs_cells[sx][sy], fill="green")
        canvas_dfs.itemconfig(dfs_cells[gx][gy], fill="red")
        update_stats_labels()

    # bind buttons
    btn_next.config(command=on_next)
    btn_run.config(command=on_run)
    btn_pause.config(command=on_pause)
    btn_reset.config(command=on_reset)

    # show initial stats
    update_stats_labels()

    root.mainloop()


# Allow running as script
if __name__ == "__main__":
    # Example grid (0 free, 1 obstacle)
    example_grid = [
        [0,0,0,1,0,0],
        [0,1,0,1,0,0],
        [0,1,0,0,0,0],
        [0,0,0,1,0,0],
        [1,1,0,0,0,0]
    ]
    start = (0,0)
    goal = (4,5)
    run_gui(example_grid, start, goal)
