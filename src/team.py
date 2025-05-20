from src.robot import RobotCooperative, RobotSelfInterested, Context
from src.objects import Empty



class CooperativeTeam:
    """
    This class represents a team of cooperative robots.
    """
    def __init__(self, grid: list, retrive_pointX: int, retrive_pointY: int):
        self.members : list[RobotCooperative] = []
        self.memory = []
        self.grid = grid
        self.context = Context()
        self.context.retrive_pointX = retrive_pointX
        self.context.retrive_pointY = retrive_pointY
        self.context.discovered_items = []
        self.context.robots = self.members

    def add_member(self, member : RobotCooperative):
        """
        Adds a member to the team.
        :param member: The cooperative robot to be added.
        """
        member.gridX = len(self.grid)
        member.gridY = len(self.grid[0])
        self.members.append(member)
        self.context.robots = self.members
        return True

    def initMemory(self,x: int,y: int):
        """
        Initializes the memory of the team.
        :param x: The number of rows in the grid.
        :param y: The number of columns in the grid.
        """
        self.memory = [[0 for _ in range(y)] for _ in range(x)]
        for robot in self.context.robots:
            robot.updateMemory(self.grid, self.memory, self.context)
            robot.get_target(self.context)

    def getMemory(self):
        return self.memory

    def turn (self):
        """
        Executes a turn for each member of the team.
        """
        for member in self.members:
            val = member.move(self.grid, self.memory, self.context)
            if val is not None:
                x = val[0]
                y = val[1]
                #print("x, y", x, y)
                self.grid[x][y] = Empty()

    def getScore(self):
        return self.context.score




class SelfInterestedTeam:
    """
    This class represents a team of self-interested robots.
    """
    def __init__(self, grid: list, retrive_pointX: int, retrive_pointY: int):
        self.members : list[RobotSelfInterested] = []
        self.grid = grid
        self.context = Context()
        self.context.retrive_pointX = retrive_pointX
        self.context.retrive_pointY = retrive_pointY
    def add_member(self, member : RobotSelfInterested):
        """
        Adds a member to the team.
        :param member: The self-interested robot to be added.
        """
        member.gridX = len(self.grid)
        member.gridY = len(self.grid[0])
        member.initMemory(self.grid)
        self.members.append(member)
        return True

    def turn (self):
        """
        Executes a turn for each member of the team.
        """
        for member in self.members:
            val = member.move(self.grid, self.context)
            if val is not None:
                x = val[0]
                y = val[1]
                self.grid[x][y] = Empty()


    def getScore(self):
        return self.context.score
