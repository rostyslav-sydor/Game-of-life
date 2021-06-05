import pygame
import pygame_gui
from pygame.locals import *
import sys
from time import time, time_ns
from copy import copy
import os

pygame.init()

WIDTH = 1280
GRID_WIDTH = 5 * WIDTH // 6

HEIGHT = 720

CELL_SIZE = 15

GPS = 3

DISPLAY = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Of Life")
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

CLOCK = pygame.time.Clock()
FPS = 200

WHITE = [255, 255, 255]
BLACK = [0, 0, 0]
PURPLE = [118, 26, 188]
LIGHT = [80, 0, 215]

class GameBoard:
    def __init__(self, width, height):
        self.width = (5*width//6) + 2    # adding 2 for border around the board
        self.height = height + 2
        self.size = self.width * self.height
        self.board = [0 for _ in range(self.size)]
        self.neighbors = [0 for _ in range(self.size)]
        self.changelist = set()
        self.templates = {}
        self.pause = False
        self.input = False
        self.load = None

        self.calculateBorder()
        self.initControls()

    def linearize(self, x, y):
        """Translating 2D coordinates to 1D"""
        return x + y * self.width
    
    def changeState(self, row, col):
        i = self.linearize(row, col)
        self.board[i] = int(not self.board[i])
        self.recalculateChangelist()

    def calculateBorder(self):
        """Calculate indices for border cells"""
        self.border = set()
        for i in range(self.size):
            if i < self.width or\
               i > self.size - self.width or\
               i % self.width == 0 or\
               i % self.width == self.width-1:
                self.border.add(i)

    def recalculateChangelist(self):
        """Completely rebuilds changelist"""
        for x in range(self.width):
            for y in range(self.height):
                i = self.linearize(x, y)
                if self.board[i]:
                    self.changelist.add(i)
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
        return [index - 1 - self.width, index - self.width, index + 1 - self.width,         # 0  1  2  3  4
                                                                                            # 5  6  7  8  9
                        index - 1,                                  index + 1,              # 10 11 12 13 14
                                                                                            # 15 16 17 18 19
                index - 1 + self.width, index + self.width, index + 1 + self.width  ]       # 20 21 22 23 24

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

    def initControls(self):
        rel_x = GRID_WIDTH
        self.back = pygame.Rect(GRID_WIDTH, 0, WIDTH - GRID_WIDTH, HEIGHT)
        template_folder = []
        try:
            path = os.path.abspath("data\\templates")
            template_folder = os.listdir(path)
        except FileNotFoundError:
            print("Could not find data folder")

        self.buttons = []
        x = 26 * rel_x // 25
        y = 20
        w = rel_x // 8
        h = 25
        for template in template_folder:
            self.templates[template[:-4]] = path + '\\' + template

        names = [k for k in self.templates.keys()]
        self.loadLabel = pygame_gui.elements.UILabel(pygame.Rect((x,y), (w,h)), "Load template", manager=manager)
        self.loadMenu = pygame_gui.elements.UIDropDownMenu(options_list=names, starting_option="None", relative_rect=pygame.Rect((x,y+25), (w,h)), manager=manager)
        self.gpsSlider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect(x, 5*HEIGHT//6, w, h), start_value=GPS, value_range=(1, 100), manager=manager)
        self.gpsLabel = pygame_gui.elements.UILabel(pygame.Rect(rel_x, 7*HEIGHT//8, WIDTH//6, h), str(int(GPS)) + " generations per second", manager=manager)
        self.stepButton = pygame_gui.elements.UIButton(pygame.Rect(x, HEIGHT//3, w, h), text="Make step", manager=manager)
        self.pauseButton = pygame_gui.elements.UIButton(pygame.Rect(x, HEIGHT//2.6, w, h), text="Pause / Unpause", manager=manager)
        self.cellChanger = pygame_gui.elements.UITextEntryLine(pygame.Rect(x, 4*HEIGHT//7, w, h), manager=manager)
        self.cellChangerLabel = pygame_gui.elements.UILabel(pygame.Rect(x, 9*HEIGHT//17, w, h), "Resize board", manager=manager)


        self.UIElements = [self.loadLabel, self.loadMenu, self.gpsSlider, self.gpsLabel, self.stepButton, self.pauseButton, self.cellChanger]

    def draw(self):
        for i in self.changelist:
            if self.board[i]:
                x = ((i % self.width) - 1) * CELL_SIZE
                y = ((i // self.width) - 1) * CELL_SIZE
                
                cell = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(DISPLAY, BLACK, cell, 0)

        self.drawGrid()
    
    def drawGrid(self):
        for x in range(GRID_WIDTH//CELL_SIZE):
            pygame.draw.line(DISPLAY, BLACK, ((x+1)*CELL_SIZE, 0), ((x+1)*CELL_SIZE, HEIGHT), 1)

        for y in range((HEIGHT//CELL_SIZE)+1):
            pygame.draw.line(DISPLAY, BLACK, (0, y*CELL_SIZE-1), (GRID_WIDTH, y*CELL_SIZE-1), 1)

    def loadTemplate(self, path, y, x):
        """Loads template from .txt file"""
        with open(path) as template:
            template = template.read().split('\n')

        if x + len(template) > self.height or\
           y + len(template[0]) > self.width:
            return None

        for i, row in enumerate(template):
            for j, cell in enumerate(row):
                index = self.linearize(y+j, x+i)
                if cell == '.':
                    self.board[index] = 0
                else:
                    self.board[index] = 1

        self.recalculateChangelist()
        self.load = None # clear load buffer
        self.loadMenu.selected_option = "None"

    def user_draw(self, start_pos):
        x,y = start_pos
        i = self.linearize((x//CELL_SIZE)+1, (y//CELL_SIZE)+1)
        if i not in self.border:
            self.board[i] = self.color
            self.recalculateChangelist()

    def mouse_input(self):
        x, y = pygame.mouse.get_pos()
        x = (x // CELL_SIZE) + 1
        y = (y // CELL_SIZE) + 1
        pos = (x//CELL_SIZE, y//CELL_SIZE)
        index = self.linearize(x+1, y+1)

        self.input = True
        self.color = not self.board[index]
        if self.load:
            self.loadTemplate(self.load, x ,y)

        elif x * CELL_SIZE < GRID_WIDTH: #check if cursor is in the grid
            self.changeState(x, y)
            self.recalculateChangelist()
    
    def terminateUI(self):
        for i in self.UIElements:
            i.kill()

if __name__ == "__main__":
    board = GameBoard(WIDTH//CELL_SIZE, HEIGHT//CELL_SIZE)

    chas = 0
    counter = 0

    while True:
        DISPLAY.fill(PURPLE)

        if not board.pause:
            if time() - chas > (1 / GPS):
                board.update()
                chas = time()

        for event in pygame.event.get():
            # Draw with mouse
            if event.type == MOUSEBUTTONDOWN:
                board.mouse_input()

            manager.process_events(event)


            if event.type == MOUSEBUTTONUP:
                board.input = False

            if board.input and event.type == MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                if pos[0] <= GRID_WIDTH:
                    board.user_draw(pos)

            # Pause
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    board.pause = not board.pause

            if event.type == USEREVENT:
                if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and\
                   event.ui_element == board.loadMenu:
                        board.load = board.templates[board.loadMenu.selected_option]
                
                elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED and\
                    event.ui_element == board.gpsSlider:
                        GPS = int(board.gpsSlider.current_value)
                        board.gpsLabel.set_text(str(GPS) + " generations per second")
                
                elif event.user_type == pygame_gui.UI_BUTTON_PRESSED and\
                    event.ui_element == board.pauseButton:
                        board.pause = not board.pause

                elif event.user_type == pygame_gui.UI_BUTTON_PRESSED and\
                    event.ui_element == board.stepButton:
                        board.update()
                
                elif event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED and\
                    event.ui_element == board.cellChanger:
                        try:
                            CELL_SIZE = int(board.cellChanger.get_text())
                            board.terminateUI()
                            board = GameBoard(WIDTH//CELL_SIZE, HEIGHT//CELL_SIZE)
                        except Exception:
                            pass

            # Quit instruction
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        time_delta = CLOCK.tick(FPS)/1000.0
        manager.update(time_delta)
        manager.draw_ui(DISPLAY)

        board.draw()


        pygame.display.update()
       