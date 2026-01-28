# -------------------------------
# 1️⃣ State Space: Graph of Cities
# -------------------------------
graph = {
    "Glogow": [("Leszno", 45), ("Poznan", 90)],
    "Leszno": [("Glogow", 45), ("Poznan", 140), ("Kalisz", 130), ("Wroclaw", 100)],
    "Poznan": [("Glogow", 90), ("Leszno", 140), ("Bydgoszcz", 108), ("Kalisz", 103)],
    "Bydgoszcz": [("Poznan", 108), ("Wloclawek", 110)],
    "Wloclawek": [("Bydgoszcz", 110), ("Konin", 55)],
    "Konin": [("Wloclawek", 55), ("Plock", 130), ("Lodz", 120)],
    "Plock": [("Konin", 130), ("Warsaw", 150)],
    "Warsaw": [("Plock", 150), ("Lodz", 165), ("Radom", 105)],
    "Lodz": [("Konin", 120), ("Warsaw", 165), ("Kalisz", 160), ("Czestochowa", 128)],
    "Kalisz": [("Poznan", 103), ("Leszno", 130), ("Lodz", 160), ("Czestochowa", 120)],
    "Czestochowa": [("Kalisz", 120), ("Lodz", 128), ("Katowice", 80)],
    "Katowice": [("Czestochowa", 80), ("Kielce", 120), ("Opole", 85)],
    "Kielce": [("Katowice", 120), ("Radom", 82), ("Krakow", 120)],
    "Radom": [("Warsaw", 105), ("Kielce", 82)],
    "Krakow": [("Kielce", 120), ("Katowice", 85)],
    "Wroclaw": [("Leszno", 100), ("Opole", 90)],
    "Opole": [("Wroclaw", 90), ("Katowice", 85)]
}

# -------------------------------
# 2️⃣ Depth-First Search (DFS)
# -------------------------------
def dfs(graph, start, goal):
    """
    DFS algorithm using open (stack) and closed (visited) containers.
    Returns a path from start to goal if exists.
    """
    stack = [(start, [start])]  # open container: stack of (node, path)
    visited = set()             # closed container: visited nodes

    while stack:
        node, path = stack.pop()  # DFS: take last element
        if node == goal:
            return path           # path found
        if node not in visited:
            visited.add(node)     # mark node as visited
            for neighbor, _ in graph[node]:
                if neighbor not in visited:
                    stack.append((neighbor, path + [neighbor]))
    return None  # goal not reachable

# -------------------------------
# 3️⃣ Run DFS Example
# -------------------------------
if __name__ == "__main__":
    start_city = "Glogow"
    goal_city = "Plock"

    path = dfs(graph, start_city, goal_city)

    print("DFS Path from start to goal:", path)
    print("Number of steps:", len(path) - 1 if path else "No path found")
