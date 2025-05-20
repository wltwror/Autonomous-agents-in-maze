import pygame
from util.consts import RECT_SIZE
from src.objects import Item, Wall
from util.helpers import BFSFindZero, optimalPathEstimate, distance



class Context:
    """
    Context class to hold the state of the game for each team
    """
    def __init__(self):
        self.robots = []
        self.discovered_items = []
        self.retrive_pointX = 0
        self.retrive_pointY = 0
        self.score = 0

def validate_coords(x : int, y : int, grid) -> bool:
    if 0 <= x < len(grid) and 0 <= y < len(grid[0]):
        return True
    return False

class Robot:
    """
    Robot class to represent the robot in the game
    Used as base class for ther types of robots
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.gridX = 0
        self.gridY = 0
        self.image = pygame.image.load("assets/robot.png") # Image under CC BY 4.0 from https://icon-icons.com/icon/technology-robot/113340
        self.image = pygame.transform.scale(self.image, (RECT_SIZE, RECT_SIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x * RECT_SIZE, self.y * RECT_SIZE)
        self.item = None
        self.target = None

    def moveUP(self):
        self.y -= 1
        self.rect.y -= RECT_SIZE
    def moveDOWN(self):
        self.y += 1
        self.rect.y += RECT_SIZE
    def moveLEFT(self):
        self.x -= 1
        self.rect.x -= RECT_SIZE
    def moveRIGHT(self):
        self.x += 1
        self.rect.x += RECT_SIZE

    def get_pos(self):
        return self.x, self.y

    def draw(self, screen : pygame.Surface):
        """
        Draw the robot on the screen
        :param screen: The screen to draw on
        """
        screen.blit(self.image, self.rect)
    def vision(self, grid : list) -> list:
        """
        Returns the 5x5 area around the robot
        :param grid: The grid to get the vision from
        """
        vision_area = []
        for i in range(-2, 3):
            vision_area.append([])
            for j in range(-2, 3):
                if 0 <= self.x + i < len(grid) and 0 <= self.y + j < len(grid[0]):
                    vision_area[i + 2].append(grid[self.x + i][self.y + j])
                else:
                    vision_area[i + 2].append(None)
        return vision_area
    def loc_mem_change(self, memory, x, y) -> int:
        """
        Returns the number of undiscovered cells in the 5x5 area around x, y coordinates
        :param memory: The memory to get the vision from
        :param x: The x coordinate of the robot
        :param y: The y coordinate of the robot
        """
        vision_area = []
        for i in range(-2, 3):
            vision_area.append([])
            for j in range(-2, 3):
                if 0 <= x + i < len(memory) and 0 <= y + j < len(memory[0]):
                    vision_area[i + 2].append(memory[x + i][y + j])
        number_of_undiscovered = 0
        for x in vision_area:
            for y in x:
                if y == 0:
                    number_of_undiscovered += 1
        return number_of_undiscovered

    def pickup(self, item : Item, discovered_items : list) -> bool:
        """
        Robot picks up an item
        :param item: The item to pick up
        :param discovered_items: The list of discovered items
        """
        if self.item is None:
            self.item = item
            discovered_items.remove(self.item)
            return True
        return False

    def deliver(self, context: Context):
        """
        Robot delivers an item
        :param context: The context of the game
        """
        if self.item is not None:
            context.score += 1
            self.item = None

    def count_closer_robots_in_vision(self, memory, context: Context, newX: int, newY: int) -> int:
        """
        Returns the number of robots in the 5x5 area around newX, newY coordinates that are closer to the newX, newY coordinates than to current robot
        :param memory: The memory to get the vision from
        :param context: The context of the game
        :param newX: Possible new x coordinate of the robot
        :param newY: Possbile new y coordinate of the robot
        """
        count = 0
        for i in range(-2, 3):
            for j in range(-2, 3):
                if 0 <= newX + i < len(memory) and 0 <= newY + j < len(memory[0]):
                    for robot in context.robots:
                        if robot != self and robot.x == newX + i and robot.y == newY + j:
                            if distance(newX, newY, newX + i, newY + j) < distance(self.x, self.y, newX + i, newY + j):
                                count += 1
        return count

class RobotCooperative(Robot):
    """
    RobotCooperative class to represent the cooperative robot (simple cooperative agent)
    Derived from the Robot class
    """
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.image = pygame.image.load("assets/robot.png") # Image under CC BY 4.0 from https://icon-icons.com/icon/technology-robot/113340
        self.image = pygame.transform.scale(self.image, (RECT_SIZE, RECT_SIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x * RECT_SIZE, self.y * RECT_SIZE)
    def updateMemory(self, grid : list, memory : list, context: Context):
        """
        Updates the memory of the robot by adding new vision area to the memory
        :param grid: The grid to get the vision from
        :param memory: The memory to update
        :param context: The context of the game
        """
        vision = self.vision(grid)
        for i in range(len(vision)):
            for j in range(len(vision[i])):
                if isinstance(vision[i][j], Item) and vision[i][j] not in context.discovered_items:
                    #print("discovered item")
                    context.discovered_items.append(vision[i][j])
        pos = self.get_pos()
        for i in range(-2, 3):
            for j in range(-2, 3):
                if 0 <= pos[0] + i < len(grid) and 0 <= pos[1] + j < len(grid[0]):
                    memory[pos[0] + i][pos[1] + j] = vision[i + 2][j + 2]

    def get_target(self, context: Context):
        """
        Robot reserves a target from the discovered items
        :param context: The context of the game
        """
        for target in context.discovered_items:
            count = 0
            for robot in context.robots:
                if target == robot.item or target == robot.target:
                    count += 1
            if count == 0:
                #print("target found")
                self.target = target

    def utility(self, x : int, y : int, memory : list, context: Context):
        """
        Utility function for the robot
        :param x: The x coordinate of the robot
        :param y: The y coordinate of the robot
        :param memory: The memory to get the vision from
        :param context: The context of the game
        """
        move_score = 0
        discovered = self.loc_mem_change(memory, x, y) # utility from discovering new area
        move_score += discovered
        if x < 0 or x >= self.gridX or y < 0 or y >= self.gridY:
            return -5
        if isinstance(memory[x][y],Wall):
            return -5
        if self.item is None:
            if self.target is not None:
                pos = self.target.get_pos()
                if distance(x, y, pos[0],pos[1]) == 0:
                    move_score += 12
                elif optimalPathEstimate(memory, self.x, self.y, pos[0], pos[1]) > optimalPathEstimate(memory, x, y, pos[0], pos[1]):
                    move_score += 8
        if self.item is not None:
            if distance(x, y, context.retrive_pointX, context.retrive_pointY) == 0:
                move_score += 10
            elif optimalPathEstimate(memory, self.x, self.y, context.retrive_pointX, context.retrive_pointY) > optimalPathEstimate(memory, x, y, context.retrive_pointX, context.retrive_pointY):
                move_score += 7
        move_score -= min(3,self.count_closer_robots_in_vision(memory, context, x, y)) # utility deduction for being close to other robots, max 3

        return move_score

    def decide_action(self,grid : list, memory : list, context: Context):
        """
        Decides the action of the robot
        :param grid: The grid to get the vision from
        :param memory: The memory to update
        :param context: The context of the game
        :return: The action to take or None if no action is taken
        """
        pos = self.get_pos()
        best_utility = float('-inf')
        best_action = None
        actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for action in actions:
            new_x = pos[0] + action[0]
            new_y = pos[1] + action[1]
            if 0 <= new_x < len(grid) and 0 <= new_y < len(grid[0]):
                utility = self.utility(new_x, new_y, memory,context)
                if utility > best_utility:
                    best_utility = utility
                    best_action = action
        #print(best_utility)
        if best_utility <= 0: # check path with bfs
            closest_undiscovered = BFSFindZero(memory, pos[0], pos[1])
            if closest_undiscovered is not None:
                x, y = closest_undiscovered
                Rx = pos[0]
                Ry = pos[1]
                distance = optimalPathEstimate(memory, self.x, self.y, x, y)
                if validate_coords(Rx - 1, Ry, grid) and optimalPathEstimate(memory,Rx - 1, Ry, x, y) < distance and not isinstance(memory[Rx - 1][Ry], Wall):
                    best_action = (-1, 0)
                elif validate_coords(Rx + 1, Ry, grid) and optimalPathEstimate(memory,Rx + 1, Ry, x, y) < distance and not isinstance(memory[Rx + 1][Ry], Wall):
                    best_action = (1, 0)
                elif validate_coords(Rx, Ry - 1, grid) and optimalPathEstimate(memory,Rx, Ry - 1, x, y) < distance and not isinstance(memory[Rx][Ry - 1], Wall):
                    best_action = (0, -1)
                elif validate_coords(Rx, Ry + 1, grid) and optimalPathEstimate(memory,Rx, Ry + 1, x, y) < distance and not isinstance(memory[Rx][Ry + 1], Wall):
                    best_action = (0, 1)
        if best_utility < -4:
            best_action = None
        #print("best: ",best_utility)
        return best_action

    def move(self, grid: list, memory: list, context: Context):
        """
        Moves the robot in the grid
        :param grid: The grid to move in
        :param memory: The memory to update
        :param context: The context of the game
        """
        action = self.decide_action(grid, memory, context)
        if action:
            if action[0] == -1:
                self.moveLEFT()
                self.updateMemory(grid, memory, context)
            elif action[0] == 1:
                self.moveRIGHT()
                self.updateMemory(grid, memory, context)
            elif action[1] == -1:
                self.moveUP()
                self.updateMemory(grid, memory, context)
            elif action[1] == 1:
                self.moveDOWN()
                self.updateMemory(grid, memory, context)
            else:
                return

        if self.target and memory[self.target.x][self.target.y] != self.target:
            context.discovered_items.remove(self.target)
            self.target = None

        #print(self.item, self.target)
        if self.target is None and self.item is None:
            self.get_target(context)

        if self.target is not None:
            if self.target.x == self.x and self.target.y == self.y:
                #print("picked up item")
                self.pickup(self.target, context.discovered_items)
                self.target = None
                return self.x, self.y
        elif self.item is not None:
            if self.x == context.retrive_pointX and self.y == context.retrive_pointY:
                self.deliver(context)
                self.item = None
                self.target = None


class RobotSelfInterested(Robot):
    """
    RobotSelfInterested class to represent the self interested robot (simple self interested agent)
    Derived from the Robot class
    """
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.image = pygame.image.load("assets/robot2.png") # Image under CC BY 4.0 (colors inverted) from https://icon-icons.com/icon/technology-robot/113340
        self.image = pygame.transform.scale(self.image, (RECT_SIZE, RECT_SIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x * RECT_SIZE, self.y * RECT_SIZE)
        self.discovered_items = []
    def updateMemory(self, grid: list):
        """
        Updates the memory of the robot by adding new vision area to the memory
        Uses does not share the memory with other robots
        :param grid: The grid to get the vision from
        """
        vision = self.vision(grid)
        for i in range(len(vision)):
            for j in range(len(vision[i])):
                if isinstance(vision[i][j], Item) and vision[i][j] not in self.discovered_items:
                    #print("discovered item")
                    self.discovered_items.append(vision[i][j])
        pos = self.get_pos()
        for i in range(-2, 3):
            for j in range(-2, 3):
                if 0 <= pos[0] + i < len(grid) and 0 <= pos[1] + j < len(grid[0]):
                    self.memory[pos[0] + i][pos[1] + j] = vision[i + 2][j + 2]


    def initMemory(self,grid: list):
        """
        Initializes the memory of the robot
        :param grid: The grid to get the vision from
        """
        self.memory = [[0 for _ in range(self.gridY)] for _ in range(self.gridX)]
        self.updateMemory(grid)
        self.get_target()

    def utility(self, x: int, y:int, context: Context) -> int:
        """
        Utility function for the robot
        :param x: The x coordinate of the robot
        :param y: The y coordinate of the robot
        :param context: The context of the game
        """
        move_score = 0
        discovered = self.loc_mem_change(self.memory, x, y)
        move_score += discovered // 2
        if x < 0 or x >= self.gridX or y < 0 or y >= self.gridY:
            return -1
        if isinstance(self.memory[x][y],Wall):
            return -5
        if self.item is None:
            if self.target is not None:
                pos = self.target.get_pos()
                if distance(x, y, pos[0],pos[1]) == 0:
                    move_score += 12
                elif optimalPathEstimate(self.memory, self.x, self.y, pos[0], pos[1]) > optimalPathEstimate(self.memory, x, y, pos[0], pos[1]):
                    move_score += 4
        if self.item is not None:
            if distance(x, y, context.retrive_pointX, context.retrive_pointY) == 0:
                move_score += 10
            elif optimalPathEstimate(self.memory, self.x, self.y, context.retrive_pointX, context.retrive_pointY) > optimalPathEstimate(self.memory, x, y, context.retrive_pointX, context.retrive_pointY):
                move_score += 7

        move_score -= min(3,self.count_closer_robots_in_vision(self.memory, context, x, y)) # utility deduction for being close to other robots, max 3

        return move_score


    def decide_action(self,grid, context: Context):
        """
        Decides the action of the robot
        :param grid: The grid to get the vision from
        :param context: The context of the game
        :return: The action to take or None if no action is taken
        """
        pos = self.get_pos()
        best_utility = float('-inf')
        best_action = None
        actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for action in actions:
            new_x = pos[0] + action[0]
            new_y = pos[1] + action[1]
            if 0 <= new_x < len(grid) and 0 <= new_y < len(grid[0]):
                utility = self.utility(new_x, new_y,context)
                if utility > best_utility:
                    best_utility = utility
                    best_action = action

        if best_utility <= 0:
            closest_undiscovered = BFSFindZero(self.memory, pos[0], pos[1])
            if closest_undiscovered is not None:
                x, y = closest_undiscovered
                Rx = pos[0]
                Ry = pos[1]
                distance = optimalPathEstimate(self.memory, self.x, self.y, x, y)
                if  validate_coords(Rx - 1, Ry, grid) and optimalPathEstimate(self.memory,Rx - 1, Ry, x, y) < distance and not isinstance(self.memory[Rx - 1][Ry], Wall):
                    best_action = (-1, 0)
                elif  validate_coords(Rx + 1, Ry, grid) and optimalPathEstimate(self.memory,Rx + 1, Ry, x, y) < distance and not isinstance(self.memory[Rx + 1][Ry], Wall):
                    best_action = (1, 0)
                elif validate_coords(Rx, Ry - 1, grid) and optimalPathEstimate(self.memory,Rx, Ry - 1, x, y) < distance and not isinstance(self.memory[Rx][Ry - 1], Wall):
                    best_action = (0, -1)
                elif validate_coords(Rx, Ry + 1, grid) and optimalPathEstimate(self.memory,Rx, Ry + 1, x, y) < distance and not isinstance(self.memory[Rx][Ry + 1], Wall):
                    best_action = (0, 1)
            if best_utility < -4:
                best_action = None
        return best_action

    def get_target(self):
        """
        Robot picks a target from his discovered items
        """
        for target in self.discovered_items:
            self.target = target
            break


    def move(self, grid: list, context: Context):
        """
        Moves the robot in the grid
        """
        action = self.decide_action(grid,context)
        if action:
            if action[0] == -1:
                self.moveLEFT()
                self.updateMemory(grid)
            elif action[0] == 1:
                self.moveRIGHT()
                self.updateMemory(grid)
            elif action[1] == -1:
                self.moveUP()
                self.updateMemory(grid)
            elif action[1] == 1:
                self.moveDOWN()
                self.updateMemory(grid)
            else:
                return
        if self.target and self.memory[self.target.x][self.target.y] != self.target:
            self.discovered_items.remove(self.target)
            self.target = None
        #print(self.item, self.target)
        if self.target is None and self.item is None:
            self.get_target()

        if self.target is not None:
            if self.target.x == self.x and self.target.y == self.y and grid[self.x][self.y] == self.target:
                self.pickup(self.target, self.discovered_items)
                self.target = None
                return self.x, self.y
        elif self.item is not None:
            if self.x == context.retrive_pointX and self.y == context.retrive_pointY:
                self.deliver(context)
                self.item = None
                self.target = None
