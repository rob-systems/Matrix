import pygame, sys
from pygame.locals import *
from random import randrange
import math
from threading import Timer
from datetime import datetime

pygame.init()

FPS = 30
FramePerSec = pygame.time.Clock()
FONT_SIZE = 16
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

font = pygame.font.SysFont("Verdana", FONT_SIZE)

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
DISPLAYSURF.fill((0,0,0))
pygame.display.set_caption("Game")

#alphabet = """           §1234567890-=qwertyuiop[]asdfghjkl;'\\`zxcvbnm,./"""
alphabet = "01"

def generate_char():
    i = randrange(len(alphabet))
    return alphabet[i]

def color_picker(color):
    if color == 'green':
        return (0,255,0)
    elif color == 'white':
        return (255,255,255)
    elif color == 'yellow':
        return (255,255,0)
    else:
        return (0,0,0)

class Grid():
    def __init__(self):
        self.columns = []
        self.iteration = 1
        self.is_paused = False
        self.keypress_handle = False
        #danger?
        self.active_keys = []
        self.active_columns = []
        for x in range(0, math.floor(SCREEN_WIDTH/FONT_SIZE)):
            self.columns.append({ 'colStr': '',
                                  #'speed': randrange(1, 3),
                                  'isCharging': False,
                                  'color': 'green',
                                  'cellsToMove': 0,
                                  'latch': 1,
                                  'latch_increased_for': 0,
                                  'cellsToMove': 0
                                  #hasControlled
                                  })
        #self.columns[1]['color'] = 'white'

    def return_n_columns(self):
        return len(self.columns)
    
    def return_user_col_pos(self):
        for x, col in enumerate(self.columns):
            if col['color'] == 'white':
                return x

    def deccelerate_col(self, col):
        self.columns[col]['latch'] -= 1

    def accelerate_col(self, col):
        if self.columns[col]['latch'] < 4:
            self.columns[col]['latch'] += 1

    def scroll_column(self, col):
        if self.columns[col]['cellsToMove'] < 3:
            self.columns[col]['cellsToMove'] += randrange(100)
        #elif self.columns[col]['cellsToMove'] > 25:
        #    self.columns[col]['latch'] += 1
        elif self.columns[col]['latch'] > 1 or self.columns[col]['latch_increased_for'] > 20:
            self.columns[col]['latch'] -= 1
            self.columns[col]['latch_increased_for'] = 0

    # RATHER THAN HAVING COLUMNS TICK HAVE SPACE THAT NEEDS TO BE MOVED THEY WILL HAVE THAT VISIBLE TICKING THOUGH?
    def shift_col_down(self, col):
        #add char
        #print(self.columns[col]['cellsToMove'])
        if (self.columns[col]['cellsToMove'] == 1):
            #print(self.active_columns, col)
            #print('helpbefore', self.active_columns)
            #print(self.active_columns.index(col))
            for x in self.active_columns:
                #print (x)
                if x == col:
                    self.active_columns.remove(x)
        elif (self.columns[col]['latch'] > 2):
            self.columns[col]['latch'] += 1
        random_char = ' ' if self.columns[col]['isCharging'] else generate_char()
        self.columns[col]['colStr'] = random_char + self.columns[col]['colStr']
        is_there = False
        for x in self.active_keys:
            for poo in x['cols']:
                if poo == col:
                    is_there = True
        if not is_there:
            self.columns[col]['cellsToMove'] -= 1
        #if self.columns[col]['cellsToMove'] == 0 and self.active_keys
        if len(self.columns[col]['colStr']) > SCREEN_HEIGHT/FONT_SIZE:
            a = round(len(self.columns[col]['colStr']) - (SCREEN_HEIGHT/FONT_SIZE))
            self.columns[col]['colStr'] = self.columns[col]['colStr'][:-(a + 1)]

    def shift_col_up(self, col):
        list2 = list(self.columns[col]['colStr'])
        for y, char in enumerate(list2):
            if y+1 >= len(list2):
                break
            if char == ' ' and list2[y+1] != ' ':
                list2.remove(char)
        self.columns[col]['colStr'] = ''.join(list2)

    def switch_white_col(self, direction):
        var = self.return_user_col_pos()
        if var + 1 >= SCREEN_WIDTH/FONT_SIZE and direction == 'right':
            return
        elif var - 1 < 0 and direction == 'left':
            return
        self.columns[var]['color'] = 'green'
        if direction == 'left':
            self.columns[var - 1]['color'] = 'white'
        elif direction == 'right':
            self.columns[var + 1]['color'] = 'white'

    def switch_two_cols(self, col1, col2):
        temp = self.columns[col1]
        self.columns[col1] = self.columns[col2]
        self.columns[col2] = temp
        self.mesh_two_cols(col1, col2)

    #cross two cols?
    def mesh_two_cols(self, col1, col2):
        l1 = list(self.columns[col1]['colStr'])
        l2 = list(self.columns[col2]['colStr'])
        len1 = len(l1)
        len2 = len(l2)
        for y, row in enumerate(l1):
            if randrange(2) == 1:
                temp = l1[y]
                if (y < len2 - 1):
                    l1[y] = l2[y]
                    l2[y] = temp
        self.columns[col1]['colStr'] = ''.join(l1)
        self.columns[col2]['colStr'] = ''.join(l2)

    def handle_scroll(self):
        for x, col in enumerate(self.columns):
            if not col['isCharging']:
                self.columns[x]['isCharging'] = True if randrange(15) == 1 else False
            else:
                self.columns[x]['isCharging'] = False if randrange(15) == 1 else True
            if self.current_iteration == 2 and ((col['speed'] == 2)):
                self.shift_col_down(x)
            elif self.current_iteration == 1 and ((col['speed'] == 2) or (col['speed'] == 1)):
                self.shift_col_down(x)

    #def handle_key_press(self):
    #    pressed_keys = pygame.key.get_pressed()
    #    if pressed_keys[K_LEFT] and not (pressed_keys[K_LSHIFT] or pressed_keys[K_RSHIFT]):
    #        user_col = self.return_user_col_pos()
    #        if user_col - 1 >= 0:
    #            self.switch_two_cols(user_col, user_col - 1)
    #    if pressed_keys[K_RIGHT] and not (pressed_keys[K_LSHIFT] or pressed_keys[K_RSHIFT]):
    #        user_col = self.return_user_col_pos()
    #        if user_col + 1 <= G1.return_n_columns() - 1:
    #            self.switch_two_cols(user_col, user_col + 1)
    #    if pressed_keys[K_UP] and not (pressed_keys[K_LSHIFT] or pressed_keys[K_RSHIFT]):
    #        user_col = self.return_user_col_pos()
    #        self.shift_col_up(user_col)
    #    if pressed_keys[K_DOWN] and not (pressed_keys[K_LSHIFT] or pressed_keys[K_RSHIFT]):
    #        user_col = self.return_user_col_pos()
    #        self.shift_col_down(user_col)
    #    if pressed_keys[K_SPACE]:
    #        self.is_paused = True
    #    else:
    #        self.is_paused = False
    #    if (pressed_keys[K_LSHIFT] or pressed_keys[K_RSHIFT]) and pressed_keys[K_LEFT]:
    #        G1.switch_white_col('left')
    #    if (pressed_keys[K_LSHIFT] or pressed_keys[K_RSHIFT]) and pressed_keys[K_RIGHT]:
    #        G1.switch_white_col('right')

    #def handle_key_press2(self):
    #    pressed_keys = pygame.key.get_pressed()
    #    List = ['qwertyuiopasdfghjklzxcvbnm']
        #for y in pygame.event.get():
                #print(y.key)
    #    for x in pressed_keys:
    #        if x:
    #            col = randrange(0, round(SCREEN_WIDTH/FONT_SIZE))
    #            self.scroll_column(col)

    def prep_movement(self):
        cur_time = datetime.now()
        for x, key in enumerate(self.active_keys):
            a = cur_time.strftime("%-S")
            b = key['timePressed'].strftime("%-S")
            if (int(a) - int(b)) > 1:
                for x in self.active_keys:
                    for y in x['cols']:
                        self.accelerate_col(y)
            #if int(cur_time - key['timePressed'].timestamp()) > 2:
            #    print('howdy')
            if not len(key['cols']) > 0:
                col = randrange(0, round(SCREEN_WIDTH/FONT_SIZE))
                for x, column in enumerate(self.columns):
                    if x == col:
                        column['latch'] += 1
                        pass
                #for x in self.active_columns:
                    
                self.scroll_column(col)
                key['cols'].append(col)
                self.active_columns.append(col)

    def handle_key_down(self, key):
        self.active_keys.append({'key': key, 'cols': [], 'timePressed': datetime.now()})
        
        #print(self.active_keys)

    def handle_key_up(self, key):
        #if len(self.active_keys)
        for x in self.active_keys:
            if len(x['cols']) > 0:
                self.active_columns.extend(x['cols'])
        for x in self.active_keys:
            if x['key'] == key:
                 self.active_keys.remove(x)
        
               

    def update(self):
        #self.handle_key_press1()
        #self.handle_key_press2()
        self.prep_movement()
        #print('help', self.active_columns)
        #if not self.is_paused:
            #self.handle_scroll()
        for x, col in enumerate(self.columns):
            self.columns[x]['latch_increased_for'] += 1;
            if self.columns[x]['cellsToMove'] > 0:
                if self.columns[x]['latch'] >= 1 and self.iteration == 1:
                        #print(1)
                        self.shift_col_down(x)
                if self.columns[x]['latch'] >= 2 and self.iteration == 2:
                        #print(2)
                        self.shift_col_down(x)
                if self.columns[x]['latch'] >= 3 and self.iteration == 3:
                        #print(3)
                        self.shift_col_down(x)
                if self.columns[x]['latch'] >= 4 and self.iteration == 4:
                        #print(4)
                        self.shift_col_down(x)
                
        self.iteration += 1
        if self.iteration == 5:
                self.iteration = 1

    def draw(self, screen):
        #removes previously drawn chars
        DISPLAYSURF.fill((0,0,0))
        for x, obj in enumerate(self.columns):
            for y, char in enumerate(obj['colStr']):
                color = color_picker(obj['color'])
                character = font.render(char, True, color)
                screen.blit(character, (x * FONT_SIZE,y * FONT_SIZE))

G1 = Grid()

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            #KEYDOWN
            G1.handle_key_down(event.key)
            pass

        if event.type == pygame.KEYUP:
            #KEYUP
            G1.handle_key_up(event.key)
            pass
    

    G1.update()
    G1.draw(DISPLAYSURF)
    pygame.display.update()
    FramePerSec.tick(FPS)
