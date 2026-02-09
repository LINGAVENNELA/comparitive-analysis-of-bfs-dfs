from collections import deque

def bfs(grid, start, goal):
    moves = [(1,0),(-1,0),(0,1),(0,-1)]
    q = deque([start])
    visited = {start: None}
    nodes_visited = 0

    while q:
        node = q.popleft()
        nodes_visited += 1

        if node == goal:
            path = []
            while node is not None:
                path.append(node)
                node = visited[node]
            return path[::-1], nodes_visited  # <-- return both path and nodes visited

        for dx, dy in moves:
            x, y = node[0]+dx, node[1]+dy
            if 0<=x<len(grid) and 0<=y<len(grid[0]) and grid[x][y]==0:
                if (x,y) not in visited:
                    visited[(x,y)] = node
                    q.append((x,y))

    return None, nodes_visited
