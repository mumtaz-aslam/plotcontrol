import pygame
from pygame.joystick import *
from utils.io_utils import *
from utils.colors import *
from utils.gfx_utils import *
import utils.svg_utils as svg

import sys
import time
import math
import time
import uuid
from enum import Enum

class ProgramState(Enum):
    DRAW_EYES = 1
    DRAW_NOSE = 2
    DRAW_MOUTH = 3

# Constants
DRAWING_PATH_DICT = {
    "DRAW_EYES": "drawings/eyes",
    "DRAW_NOSE": "drawings/nose",
    "DRAW_MOUTH": "drawings/mouth",
}

JOYSTICK_POLL_INTERVAL = 0.03 # Seconds
JOYSTICK_SPEED_MULTIPLIER = 3

POINTER_START_X = 50
POINTER_START_Y = 50

# Global state
pointer_x = POINTER_START_X
pointer_y = POINTER_START_Y
relative_line_segments = []

def xy_filtered(x, y):
    radius = math.sqrt(x**2 + y**2)
    return (0, 0) if radius < 0.2 else (x, y)

def start_game_loop(surface, joystick):
    global pointer_x, pointer_y, relative_line_segments
    pygame.display.update()
    program_state = ProgramState.DRAW_EYES

    lastJoystickPollTime = time.time()
    while True:
        new_events = pygame.event.get()
        for event in new_events:
            if event.type == pygame.JOYBUTTONDOWN and event.button == 0: # XBOX A
                path = svg.create_path(POINTER_START_X, POINTER_START_Y, relative_line_segments)
                fname = uuid.uuid4().hex
                folder = DRAWING_PATH_DICT[program_state.name]
                svg.save_svg([path], folder + "/" + fname + ".svg")
                relative_line_segments = []
                
                if program_state == ProgramState.DRAW_EYES:
                    program_state = ProgramState.DRAW_NOSE
                elif program_state == ProgramState.DRAW_NOSE:
                    program_state = ProgramState.DRAW_MOUTH
                elif program_state == ProgramState.DRAW_MOUTH:
                    program_state = ProgramState.DRAW_EYES
            if event.type == pygame.JOYBUTTONDOWN and event.button == 1: # XBOX B
                path = svg.create_path(POINTER_START_X, POINTER_START_Y, relative_line_segments)
                svg.save_and_open_svg(path)
                print("FooBarBaz")
            if event.type == QUIT:
                cleanup_and_exit()

        currentTime = time.time()
        timeSinceLastPoll = currentTime - lastJoystickPollTime
        if timeSinceLastPoll > JOYSTICK_POLL_INTERVAL:
            x_raw = joystick.get_axis(0)
            y_raw = joystick.get_axis(1)
            (x, y) = xy_filtered(x_raw, y_raw)
            (dx, dy) = (JOYSTICK_SPEED_MULTIPLIER*x, JOYSTICK_SPEED_MULTIPLIER*y)
            pointer_x = pointer_x + dx
            pointer_y = pointer_y + dy
            draw_pointer(surface, pointer_x, pointer_y)
            pygame.display.update()
            lastJoystickPollTime = time.time()
            if dx != 0 and dy != 0:
                relative_line_segments.append((dx, dy))

def main():
    surface = init_and_create_window()
    draw_pointer(surface, pointer_x, pointer_y)

    joystick = init_joystick()
    if joystick == None:
        cleanup_and_exit()

    start_game_loop(surface, joystick)

if __name__ == '__main__':
    main()