from src.objects import Wall, Empty, Item
from util.consts import DENSITY_COEFFICIENT
import random

def distance(x1: int, y1: int, x2:int, y2: int) -> int:
    """
    Returns the Manhattan distance between two points (x1, y1) and (x2, y2).
    """
    return abs(x1 - x2) + abs(y1 - y2)



def BFSFindZero(memory: list, x: int, y: int):
    """
    Finds closest zero in the memory
    :param memory: 2D list representing the memory
    :param x: starting x coordinate
    :param y: starting y coordinate
    :return: coordinates of the closest zero in the memory or None if not found
    """
    queue = [(x, y)]
    visited = set()
    visited.add((x, y))
    while queue:
        current_x, current_y = queue.pop(0)
        if memory[current_x][current_y] == 0:
            return current_x, current_y
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_x = current_x + dx
            new_y = current_y + dy
            if 0 <= new_x < len(memory) and 0 <= new_y < len(memory[0]) and (new_x, new_y) not in visited and not isinstance(memory[new_x][new_y], Wall):
                queue.append((new_x, new_y))
                visited.add((new_x, new_y))
    return None

def BFSShortestPathToItem(memory: list, x: int, y: int, itemX: int, itemY: int, known=True) -> int:
    """
    Returns length of the shortest path to the item
    :param memory: 2D list representing the memory
    :param x: starting x coordinate
    :param y: starting y coordinate
    :param itemX: x coordinate of the item
    :param itemY: y coordinate of the item
    :param known: if True, only guaranteed paths are considered
    """
    queue = [(x, y, 0)]  # (x, y, distance)
    visited = set()
    visited.add((x, y))
    while queue:
        current_x, current_y, distance = queue.pop(0)
        if isinstance(memory[current_x][current_y], Wall):
            continue
        if current_x == itemX and current_y == itemY:
            return distance
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_x = current_x + dx
            new_y = current_y + dy
            if 0 <= new_x < len(memory) and 0 <= new_y < len(memory[0]) and (new_x, new_y) not in visited and (validate_known_path(memory[new_x][new_y]) if known else validate_unknown_path(memory[new_x][new_y])):
                queue.append((new_x, new_y, distance + 1))
                visited.add((new_x, new_y))
    return -1


def validate_known_path(obj) -> bool:
    """
    checks if the object is a wall or empty space
    """
    if isinstance(obj, Empty) or isinstance(obj, Item):
        return True
    return False

def validate_unknown_path(obj) -> bool:
    """
    checks if the object is a wall, empty space or 0 (=unknown)
    """
    if isinstance(obj, Empty) or isinstance(obj, Item) or obj == 0:
        return True
    return False

def optimalPathEstimate(memory: list, x: int, y: int, itemX: int, itemY: int) -> int:
    """
    Returns estimate of the optimal path length to the item based on the density of the walls
    :param memory: 2D list representing the memory
    :param x: starting x coordinate
    :param y: starting y coordinate
    :param itemX: x coordinate of the item
    :param itemY: y coordinate of the item
    """
    known = BFSShortestPathToItem(memory, x, y, itemX, itemY, known=True)
    unknown = BFSShortestPathToItem(memory, x, y, itemX, itemY, known=False)
    if known * DENSITY_COEFFICIENT > unknown:
        return known
    return unknown

class Node:
    """
    Node class for DFS-based pathfinding
    """
    def __init__(self, x, y, prev):
        self.x = x
        self.y = y
        self.prev = prev

def getRandomPath(one: tuple, two: tuple, grid: list):
    """
    DFS-based algorithm to get a random path between two points
    sets elements on the path to 1
    adds neighbors to stack in random order favoring neighbors closer to the target
    :param one: starting point
    :param two: target point
    :param grid: 2D list representing the grid
    """
    grid[one[0]][one[1]] = 1
    grid[two[0]][two[1]] = 1
    # DFS with random choice
    stack = [Node(one[0], one[1], None)]
    visited = set()
    visited.add(one)
    current = one
    while stack:
        current = stack.pop()
        if current.x == two[0] and current.y == two[1]:
            # reconstruct path
            while current.prev is not None:
                grid[current.x][current.y] = 1
                current = current.prev
            return
        x, y = current.x, current.y
        neighbors = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]

        #print("neighbors", neighbors)
        neighbors = shuffleNeighbors(current, neighbors, two, grid)
        for neighbor in neighbors:
            nx, ny = neighbor
            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and neighbor not in visited:
                stack.append(Node(nx, ny, current))
                visited.add(neighbor)


def shuffleNeighbors(current: Node, neighbors: list, target: tuple, grid: list) -> list:
    """
    sorts neighbors of a location in random order
    uses weighted rulette to choose order of neighbors
    closer to target weight = 15
    else weight = 1
    ensures "short" path but not necessarily the shortest
    :param current: current node
    :param neighbors: list of neighbors
    :param target: target coordinates
    :param grid: 2D list representing the grid
    """
    distances = []
    current_distance = distance(current.x, current.y, target[0], target[1])
    for neighbor in neighbors:
        nx, ny = neighbor
        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
            neighbor_distance = distance(nx, ny, target[0], target[1])
            if neighbor_distance < current_distance:
                distances.append((neighbor, 15))
            else:
                distances.append((neighbor, 1))
    # weighted rulette
    total_weight = sum(weight for _, weight in distances)
    if total_weight == 0:
        return neighbors
    weights = [weight / total_weight for _, weight in distances]
    # sort by weight
    sampled = random.choices([n for n, _ in distances], weights=weights, k=len(distances))
    seen = set()
    shuffled_neighbors = []
    for n in sampled:
        if n not in seen:
            shuffled_neighbors.append(n)
            seen.add(n)
        if len(shuffled_neighbors) == len(distances):
            break

    return shuffled_neighbors















