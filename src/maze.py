import pygame
from src.robot import Robot, RobotCooperative, RobotSelfInterested
from util.consts import DENSITY_COEFFICIENT
from src.objects import Empty, Item, Wall
import random
from util.helpers import getRandomPath


class Maze:
    """
    Class representing the 2D maze.
    """
    def __init__(self, x : int, y: int):
        self.x = x
        self.y = y
        self.maze = [[Empty() for _ in range(y)] for _ in range(x)]
        self.robots = []
        self.itemCount = 0
        self.deliveryPoints = []

    def get(self, x: int, y: int):
        """
        Returns the item at the given coordinates in the maze.
        :param x: x coordinate of the item
        :param y: y coordinate of the item
        """
        return self.maze[x][y]
    def set(self, x: int, y: int, item):
        """
        Sets the item at the given coordinates in the maze.
        :param x: x coordinate of the item
        :param y: y coordinate of the item
        """
        item.x = x
        item.y = y
        self.maze[x][y] = item
    def add_robot(self, robot: Robot):
        self.robots.append(robot)

    def draw(self, screen: pygame.Surface):
        """
        Draws the maze on the given surface.
        :param screen: surface to draw on
        """
        for x in range(len(self.maze)):
            for y in range(len(self.maze[0])):
                self.maze[x][y].draw(screen, x, y)
        for robot in self.robots:
            robot.draw(screen)


    def create_paths(self):
        """
        Ensures that there are paths between all items, robots and delivery points.
        """
        grid_with_paths = [[Empty() for _ in range(self.y)] for _ in range(self.x)]
        for x in range(len(self.maze)):
            for y in range(len(self.maze[0])):
                grid_with_paths[x][y] = self.maze[x][y]
        all_objects = []
        # add items
        for x in range(len(self.maze)):
            for y in range(len(self.maze[0])):
                if not isinstance(self.maze[x][y], Empty):
                    all_objects.append((x, y))
        # add robots
        for robot in self.robots:
            all_objects.append((robot.x, robot.y))
        # add delivery points
        for point in self.deliveryPoints:
            all_objects.append(point)
        # pick 2 random points from all_objects
        one = random.choice(all_objects)
        two = random.choice(all_objects)
        all_objects.remove(one)
        while one == two:
            two = random.choice(all_objects)
        all_objects.remove(two)
        processed = []
        processed.append(one)
        processed.append(two)
        # create a path between the two points
        getRandomPath(one, two, grid_with_paths)
        while(len(all_objects) > 0):
            # pick a random point from all_objects
            next = random.choice(all_objects)
            all_objects.remove(next)
            # pick a random point from processed
            two = random.choice(processed)
            getRandomPath(next, two, grid_with_paths)
            processed.append(next)

        return grid_with_paths



    def generate(self, itemCount: int, robotCount: int):
        """
        Generates the maze with the given number of items and robots.
        :param itemCount: number of items to generate
        :param robotCount: number of robots to generate
        """
        # add all robots, items and delivery points to the maze
        self.itemCount = itemCount

        for i in range(itemCount):
            while True:
                x = random.randint(0, self.x - 1)
                y = random.randint(0, self.y - 1)
                if isinstance(self.maze[x][y], Empty):
                    break
            item = Item()
            self.set(x, y, item)
        for i in range(2):
            while True:
                x = random.randint(0, self.x - 1)
                y = random.randint(0, self.y - 1)
                if isinstance(self.maze[x][y], Empty):
                    break
            self.deliveryPoints.append((x, y))

        for i in range(robotCount * 2):
            while True:
                x = random.randint(0, self.x - 1)
                y = random.randint(0, self.y - 1)
                if isinstance(self.maze[x][y], Empty):
                    if ((x, y) not in self.deliveryPoints):
                        break
            if i % 2 == 0:
                self.add_robot(RobotCooperative(x, y))
            else:
                self.add_robot(RobotSelfInterested(x, y))

        # make sure paths are clear
        paths = self.create_paths()
        # add walls to the maze
        nonempty = 0
        for x in range(len(paths)):
            for y in range(len(paths[0])):
                if not isinstance(paths[x][y], Empty):
                    nonempty += 1
        grid_size = len(paths) * len(paths[0])
        left_over = grid_size - nonempty
        wallCount = left_over * (DENSITY_COEFFICIENT - 1)
        for i in range(int (wallCount)):
            while True:
                x = random.randint(0, self.x - 1)
                y = random.randint(0, self.y - 1)
                if isinstance(paths[x][y], Empty) and isinstance(self.maze[x][y], Empty):
                    break
            self.set(x, y, Wall())









