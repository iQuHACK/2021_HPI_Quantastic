import pygame
import time
from starbattle import full_solution, verify_solution
from queue import Queue
from threading import Thread

STATE_PLAYING = 0
STATE_PLAYING_QPU_VALID = 1
STATE_PLAYING_QPU_INVALID = 2
STATE_WON_BEFORE_QPU = 3
STATE_WON_QPU_VALID = 4
STATE_WON_QPU_INVALID = 5
STATE_SHOW_SOLUTION = 6
STATE_END = 7

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 200, 0)
GREY = (200, 200, 200)
RED = (255, 17, 0)

# Define the size of the Player window
size = [800, 800]

FPS = 60

# Calculate the height of the info box and the button at the bottom
info_height = round(size[1] / 10)
button_height = round(size[1] / 5)

# Update the height accordingly
size[1] += info_height + button_height

size = tuple(size)


def full_solve_queue(q, cells, num_stars):
    q.put(full_solution(cells, num_stars))


def draw_board(screen, cells, marked_cells, show_solution, solution, delta_x, delta_y):
    """ Draws a board to the screen. It takes the following parameters:
    screen: The screen the board should be drawn to
    cells: The original cells, with the information about the blocks
    marked_cells: The Cells marked by the user
    show_solution: Bool if the user wants the solution to be displayed
    delta_y: height of a cell
    delta_x: width of a cell
    """
    sysfont = pygame.font.get_default_font()
    plus_font = pygame.font.SysFont(sysfont, round(size[1]/7))
    mark = plus_font.render("+", True, BLACK)
    start_y = info_height
    for y, row in enumerate(cells):
        start_x = 0
        for x, _ in enumerate(row):
            if show_solution and solution[y][x] == 1:
                pygame.draw.rect(screen, GREEN, [
                                 start_x, start_y, delta_x, delta_y])

            if marked_cells[y][x] == 1:
                text_rect = mark.get_rect(
                    center=(start_x + (delta_x/2), start_y + (delta_y/2)))
                screen.blit(mark, text_rect)

            if y >= 1:
                pygame.draw.line(screen, BLACK, [start_x, start_y],
                                 [start_x + delta_x, start_y], 2 if cells[y-1][x] == cells[y][x] else 5)
            if x >= 1:
                pygame.draw.line(screen, BLACK, [start_x, start_y],
                                 [start_x, start_y+delta_y], 2 if cells[y][x-1] == cells[y][x] else 5)
            start_x += delta_x
        start_y += delta_y


def draw_results(screen, qpu_info, your_time, result_text):

    # Calculate fontsize
    font_size = round(size[1]/20)

    # Get sysfont
    sysfont = pygame.font.get_default_font()
    font = pygame.font.SysFont(sysfont, font_size)

    # Render PopUp
    pygame.draw.rect(
        screen, WHITE, [size[0]/4, size[1]/2 - 1.5 * font_size, size[0]/2, font_size*3])
    pygame.draw.rect(
        screen, BLACK, [size[0] / 4, size[1] / 2 - 1.5*font_size, size[0] / 2, font_size * 3], 5)

    # Render QPU Text
    qpu_text = font.render(qpu_info, True, BLACK)
    text_rect_qpu_time = qpu_text.get_rect(
        center=(size[0] / 2, size[1] / 2 + font_size))
    screen.blit(qpu_text, text_rect_qpu_time)

    # Render your Time
    your_text = font.render(your_time, True, BLACK)
    text_rect_your_time = your_text.get_rect(center=(size[0] / 2, size[1] / 2))
    screen.blit(your_text, text_rect_your_time)

    # Render message
    win_text = font.render(result_text, True, BLACK)
    text_rect_you_won = win_text.get_rect(
        center=(size[0] / 2, size[1] / 2 + -1 * font_size))
    screen.blit(win_text, text_rect_you_won)


def draw_info_error(screen, error, info, font):
    error_text = font.render(error, True, BLACK)
    text_rect = error_text.get_rect(
        center=(size[0]/4, size[1]-(button_height/2)))
    screen.blit(error_text, text_rect)

    info_text = font.render(info, True, BLACK)
    info_rect = info_text.get_rect(center=(size[0]/2, info_height / 2))
    screen.blit(info_text, info_rect)
    pygame.draw.line(screen, BLACK, [0, info_height], [
                     size[0], info_height])


def draw_button(screen, button_color, text, font):
    pygame.draw.rect(
        screen, button_color, [size[0] / 2, size[1] - button_height, size[0] / 2, button_height])

    display_text = font.render(text, True, BLACK)
    text_rect = display_text.get_rect(
        center=(size[0]/4*3, size[1]-(button_height/2)))
    screen.blit(display_text, text_rect)


def loop(cells, num_stars):
    """ This loop draws a gui, specified by cells and num_stars
    cells: The original cells with the information about the blocks
    num_stars: The number of stars the player has to mark in every block, column and row
    """
    state = STATE_PLAYING
    start = time.time()
    qpu_end = time.time()
    user_end = time.time()

    q = Queue()
    thread = Thread(target=full_solve_queue, args=(q, cells, num_stars))
    thread.start()
    pygame.init()
    screen = pygame.display.set_mode(size)
    width = len(cells)

    marked_cells = [[0]*width for _ in range(width)]
    solution = [[0]*width for _ in range(width)]
    delta_x = size[0] / width
    delta_y = (size[1] - button_height - info_height) / width
    # The loop will carry on until the user exit the game (e.g. clicks the close button).
    sysfont = pygame.font.get_default_font()
    font = pygame.font.SysFont(sysfont, round(size[1]/22.5))
    # The clock will be used to control how fast the screen updates
    clock = pygame.time.Clock()
    if num_stars == 1:
        info = "You need {} star per block, row and column".format(num_stars)
    else:
        info = "You need {} stars per block, row and column".format(
            num_stars)
    error = ""
    solution = []
    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                state = STATE_END  # Flag that we are done so we exit this loop
            if event.type == pygame.MOUSEBUTTONDOWN:
                if mouse[1] < size[1] - button_height and mouse[1] > info_height and state <= STATE_PLAYING_QPU_INVALID:
                    cell_y = int((mouse[1] - info_height) / delta_y)
                    cell_x = int(mouse[0] / delta_x)

                    marked_cells[cell_y][cell_x] = 0 if marked_cells[cell_y][cell_x] == 1 else 1
                    valid, error = verify_solution(
                        num_stars, cells, marked_cells)
                    if valid:
                        if state == STATE_PLAYING:
                            state = STATE_WON_BEFORE_QPU
                        elif state == STATE_PLAYING_QPU_VALID:
                            state = STATE_WON_QPU_VALID
                        elif state == STATE_PLAYING_QPU_INVALID:
                            state = STATE_WON_QPU_INVALID
                        user_end = time.time()
                if mouse[0] >= size[0]/2 and mouse[1] >= size[1]-button_height and state == STATE_PLAYING_QPU_VALID:
                    state = STATE_SHOW_SOLUTION

        if state == STATE_END:
            break

        if q.qsize() > 0:
            solution = q.get()
            qpu_valid, _ = verify_solution(num_stars, cells, solution)
            if qpu_valid:
                if state == STATE_PLAYING:
                    state = STATE_PLAYING_QPU_VALID
                elif state == STATE_WON_BEFORE_QPU:
                    state = STATE_WON_QPU_VALID
            else:
                if state == STATE_PLAYING:
                    state = STATE_PLAYING_QPU_INVALID
                elif state == STATE_WON_BEFORE_QPU:
                    state = STATE_WON_QPU_INVALID
            qpu_end = time.time()

        screen.fill(WHITE)
        draw_board(screen, cells, marked_cells, state == STATE_SHOW_SOLUTION or state ==
                   STATE_WON_QPU_VALID, solution, delta_x, delta_y)
        draw_info_error(screen, error, info, font)

        if state == STATE_PLAYING_QPU_VALID:
            button_color = DARKGREEN
            if mouse[0] >= size[0]/2 and mouse[1] >= size[1]-button_height:
                button_color = GREEN
            draw_button(screen, button_color, "Show solution", font)
        elif state == STATE_PLAYING_QPU_INVALID or state == STATE_WON_QPU_INVALID:

            draw_button(screen, RED, "QPU failed", font)
        elif state == STATE_PLAYING or state == STATE_WON_BEFORE_QPU:
            draw_button(screen, GREY, "QPU is running", font)
        elif state == STATE_SHOW_SOLUTION:
            draw_button(screen, GREY, "QPU Time: {}".format(
                round(qpu_end - start, 2)), font)
        else:
            draw_button(screen, WHITE, "", font)

        pygame.draw.rect(
            screen, BLACK, [0, size[1]-button_height, size[0], size[1]], width=3)

        if state == STATE_WON_BEFORE_QPU:
            draw_results(screen, "QPU didn't finish",
                         "Your time: {}s".format(round(user_end-start, 2)), "You WON!")
        elif state == STATE_WON_QPU_VALID:
            draw_results(screen, "QPU time: {}s".format(round(qpu_end-start, 2)),
                         "Your time: {}s".format(round(user_end-start, 2)), "You WON!")
        elif state == STATE_WON_QPU_INVALID:
            draw_results(screen, "QPU failed!", "Your time: {}s".format(round(
                user_end - start, 2)), "You WON!")

        # Update display
        pygame.display.flip()

        clock.tick(FPS)

    # Once we have exited the main program loop we can stop the game engine:
    pygame.quit()
