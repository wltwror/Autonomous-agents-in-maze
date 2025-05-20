import pygame
from util.consts import RECT_SIZE



class Empty:
    """
    Class representing an empty cell in the grid.
    """
    def __init__(self):
        self.inmemory = False
        self.isDeliveryPoint1 = False
        self.isDeliveryPoint2 = False
        self.x = 0
        self.y = 0
    def draw(self, screen: pygame.Surface, x: int, y: int):
        """
        Draw the empty cell on the screen.
        :param screen: The pygame surface to draw on.
        :param x: The x-coordinate of the cell.
        :param y: The y-coordinate of the cell.
        """
        if self.isDeliveryPoint1:
            # blue
            pygame.draw.rect(screen, (0, 0, 255), (x * RECT_SIZE, y * RECT_SIZE, RECT_SIZE, RECT_SIZE))
        elif self.isDeliveryPoint2:
            # orange
            pygame.draw.rect(screen, (255, 165, 0), (x * RECT_SIZE, y * RECT_SIZE, RECT_SIZE, RECT_SIZE))

        elif  self.inmemory:
            # green
            pygame.draw.rect(screen, (0, 255, 0), (x * RECT_SIZE, y * RECT_SIZE, RECT_SIZE, RECT_SIZE))
        pygame.draw.rect(screen, (0, 0, 0), (x * RECT_SIZE, y * RECT_SIZE, RECT_SIZE, RECT_SIZE), 1)

class Wall:
    """
    Class representing a wall in the grid.
    """
    def __init__(self):
        self.x = 0
        self.y = 0
    def draw(self, screen: pygame.Surface, x: int, y: int):
        """
        Draw the wall on the screen.
        :param screen: The pygame surface to draw on.
        :param x: The x-coordinate of the wall.
        :param y: The y-coordinate of the wall.
        """
        pygame.draw.rect(screen, (0, 0, 0), (x * RECT_SIZE, y * RECT_SIZE, RECT_SIZE, RECT_SIZE))

class Item:
    """
    Class representing an item in the grid. Robots can pick up items.
    """
    def __init__(self):
        self.x = 0
        self.y = 0
    def draw(self, screen: pygame.Surface, x: int, y: int):
        """
        Draw the item on the screen.
        :param screen: The pygame surface to draw on.
        :param x: The x-coordinate of the item.
        :param y: The y-coordinate of the item.
        """
        pygame.draw.circle(screen, (255, 0, 0), (x * RECT_SIZE + RECT_SIZE // 2, y * RECT_SIZE + RECT_SIZE // 2), RECT_SIZE // 4)

    def get_pos(self) -> tuple:
        return self.x, self.y
