import pygame
from src.maze import Maze
from src.objects import Empty
from src.robot import RobotCooperative, RobotSelfInterested
from src.team import CooperativeTeam, SelfInterestedTeam
from util.consts import MAZE_X, MAZE_Y, RECT_SIZE, ITEM_COUNT, AUTOMOVE_DELAY, ROBOT_COUNT


def pygame_simulation():
    """
    Runs a pygame simulation
    """
    maze = Maze(MAZE_X, MAZE_Y)

    maze.generate(itemCount=ITEM_COUNT, robotCount=ROBOT_COUNT//2)
    team1 = CooperativeTeam(maze.maze, maze.deliveryPoints[0][0], maze.deliveryPoints[0][1])
    team2 = SelfInterestedTeam(maze.maze, maze.deliveryPoints[1][0], maze.deliveryPoints[1][1])
    for i in maze.robots:
        if isinstance(i, RobotCooperative):
            team1.add_member(i)
        elif isinstance(i, RobotSelfInterested):
            team2.add_member(i)

    team1.initMemory(maze.x, maze.y)
    i = 0
    for point in maze.deliveryPoints:
        if i % 2 == 0:
            maze.maze[point[0]][point[1]].isDeliveryPoint1 = True
        else:
            maze.maze[point[0]][point[1]].isDeliveryPoint2 = True
        i += 1
    pygame.init()
    screen = pygame.display.set_mode((MAZE_X * RECT_SIZE, MAZE_Y * RECT_SIZE))
    clock = pygame.time.Clock()


    running = True
    automove = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    team1.turn()
                    team2.turn()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: # display the memory of team1
                    for i in range(maze.x):
                        for j in range(maze.y ):
                            if isinstance(team1.memory[i][j], Empty):
                                maze.maze[i][j].inmemory = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    automove = not automove
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE: # toggle off memory display
                    for i in range(maze.x):
                        for j in range(maze.y ):
                            if isinstance(team1.memory[i][j], Empty):
                                maze.maze[i][j].inmemory = False
                    for i in range(maze.x):
                        for j in range(maze.y ):
                            for k in range(len(team2.members)):
                                if isinstance(team2.members[k].memory[i][j], Empty):
                                    maze.maze[i][j].inmemory = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT: # display combined team2 memory
                    for i in range(maze.x):
                        for j in range(maze.y ):
                            for k in range(len(team2.members)):
                                if isinstance(team2.members[k].memory[i][j], Empty):
                                    maze.maze[i][j].inmemory = True
        if team1.context.score + team2.context.score == ITEM_COUNT:
            running = False
        if automove and running:
            team1.turn()
            team2.turn()
            # wait for AUTOMOVE_DELAY seconds
            pygame.time.delay(int(AUTOMOVE_DELAY * 1000))

        screen.fill((255, 255, 255))
        maze.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    print("Team 1: ", team1.getScore())
    print("Team 2: ", team2.getScore())

def team_winrate(runs: int):
    """
    Runs the simulation runs-times and returns wins for both teams, draws, cumulative score and total turns of the simulation
    """
    team1Win = 0
    team2Win = 0
    draw = 0
    team1Score = 0
    team2Score = 0
    totalTurns = 0
    for i in range(runs):
        maze = Maze(MAZE_X, MAZE_Y)

        maze.generate(itemCount=ITEM_COUNT, robotCount=ROBOT_COUNT//2)
        team1 = CooperativeTeam(maze.maze, maze.deliveryPoints[0][0], maze.deliveryPoints[0][1])
        team2 = SelfInterestedTeam(maze.maze, maze.deliveryPoints[1][0], maze.deliveryPoints[1][1])
        for i in maze.robots:
            if isinstance(i, RobotCooperative):
                team1.add_member(i)
            elif isinstance(i, RobotSelfInterested):
                team2.add_member(i)

        team1.initMemory(maze.x, maze.y)
        i = 0
        for point in maze.deliveryPoints:
            if i % 2 == 0:
                maze.maze[point[0]][point[1]].isDeliveryPoint1 = True
            else:
                maze.maze[point[0]][point[1]].isDeliveryPoint2 = True
            i += 1
        while True:
            totalTurns += 1
            team1.turn()
            team2.turn()
            if team1.context.score + team2.context.score == ITEM_COUNT:
                team1Score += team1.getScore()
                team2Score += team2.getScore()
                if team1.getScore() > team2.getScore():
                    team1Win += 1
                elif team1.getScore() < team2.getScore():
                    team2Win += 1
                else:
                    draw += 1
                break
    print("Team 1 wins: ", team1Win)
    print("Team 2 wins: ", team2Win)
    print("Draw: ", draw)
    print("Team 1 Score: ", team1Score)
    print("Team 2 Score: ", team2Score)
    print("Total Turns: ", totalTurns)


