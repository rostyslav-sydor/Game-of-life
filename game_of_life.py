import pygame
from pygame.locals import *
import sys
from time import time, time_ns
from copy import copy

pygame.init()

WIDTH = 1680
HEIGHT = 800
CELL_SIZE = 6

DISPLAY = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Of Life")
CLOCK = pygame.time.Clock()
FPS = 200

WHITE = [255, 255, 255]
BLACK = [0, 0, 0]
PURPLE = [118, 26, 188]

class GameBoard:
    def __init__(self, width, height):
        self.width = width + 2      # adding 2 for border around the board
        self.height = height + 2
        self.size = self.width * self.height
        self.board = [0 for _ in range(self.size)]
        self.neighbors = [0 for _ in range(self.size)]
        self.changelist = set()
        
        self.calculateBorder()

    def linearize(self, x, y):
        """Translating 2D coordinates to 1D"""
        return x + y * self.width
    
    def changeColor(self, row, col):
        i = self.linearize(row, col)
        self.board[i] = int(not self.board[i])
        self.recalculateChangelist()

    def calculateBorder(self):
        """Calculate indices for border cells"""
        self.border = set()
        for i in range(self.size):
            if i < self.width or i > self.size - self.width or i % self.width == 0 or i % self.width == self.width-1:
                self.border.add(i)

    def recalculateChangelist(self):
        """Completely rebuilds changelist"""
        for x in range(self.width):
            for y in range(self.height):
                i = self.linearize(x, y)
                if self.board[i]:
                    for j in self.neighborsList(i):
                        if j not in self.border:
                            self.changelist.add(j)

    def updateChangelist(self):
        """Updates changelist based on itself"""
        tempChangelist = copy(self.changelist)

        for i in self.changelist:
            if self.countNeighborSum(i) == 0 and self.board[i] == 0: # Remove if cell is dead and has no neighbors
                tempChangelist.remove(i)

            else:
                for neighbor in self.neighborsList(i): # Add neighbors of every alive cell
                    if neighbor not in self.border:                            
                        tempChangelist.add(neighbor)

        self.changelist = tempChangelist

    def neighborsList(self, index):
        """Calculates indices of cell's neighbors """
        neighbors = [
                    index - 1 - self.width, index - self.width, index + 1 - self.width,         # 0  1  2  3  4
                                                                                                # 5  6  7  8  9
                            index - 1,                                  index + 1,              # 10 11 12 13 14
                                                                                                # 15 16 17 18 19
                    index - 1 + self.width, index + self.width, index + 1 + self.width]         # 20 21 22 23 24

        return neighbors

    def countNeighborSum(self, index):
        summ = 0
        for neighbor in self.neighborsList(index):
                summ += self.board[neighbor]
        return summ
    
    def countNeighbors(self):
        """Calculates neighbors for every cell"""
        for i in self.changelist:
            self.neighbors[i] = self.countNeighborSum(i)

    def checkRules(self):
        for i in self.changelist:
            if (self.neighbors[i] == 2 and self.board[i]) or self.neighbors[i] == 3:
                self.board[i] = 1
            else:
                self.board[i] = 0

    def update(self):
        self.updateChangelist()
        self.countNeighbors()
        self.checkRules()

    def drawGrid(self):
        for x in range((WIDTH//CELL_SIZE)+1):
            pygame.draw.line(DISPLAY, BLACK, ((x+1)*CELL_SIZE, 0), ((x+1)*CELL_SIZE, HEIGHT), 1)

        for y in range((HEIGHT//CELL_SIZE)+1):
            pygame.draw.line(DISPLAY, BLACK, (0, y*CELL_SIZE-1), (WIDTH, y*CELL_SIZE-1), 1)

    def draw(self):
        for i in self.changelist:
            if self.board[i]:
                x = ((i % self.width) - 1) * CELL_SIZE
                y = ((i // self.width) - 1) * CELL_SIZE
                
                cell = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(DISPLAY, BLACK, cell, 0)

        self.drawGrid()

    def loadTemplate(self, path, y, x):
        """Loads template from .txt file"""
        with open(path) as template:
            template = template.read().split('\n')

        for i, row in enumerate(template):
            for j, cell in enumerate(row):
                index = self.linearize(y+j, x+i)
                if cell == '.':
                    self.board[index] = 0
                else:
                    self.board[index] = 1

        board.recalculateChangelist()


if __name__ == "__main__":
    board = GameBoard(WIDTH//CELL_SIZE, HEIGHT//CELL_SIZE)

    board.loadTemplate("templates\glider-gun.txt", 10, 20)
    board.loadTemplate("templates\glider-gun.txt", 70, 20)
    board.loadTemplate("templates\glider.txt", 200, 20)

    chas = 0
    counter = 0

    while True:
        DISPLAY.fill(PURPLE)
        chass = time_ns()
        board.update()
        print(str(time_ns()-chass) + "update")
        board.draw()
        chass =time_ns()
        print(str(time_ns()-chass) + "draw")

        # Quit instruction
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        CLOCK.tick(FPS)

        #FPS counter
        if time() - chas < 1:
            counter += 1
        else:
            print(str(counter) + " generations per second")
            chas = time()
            counter = 1
