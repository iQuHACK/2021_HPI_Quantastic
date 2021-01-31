import pygame
import time
from starbattle import full_solution, verify_solution
from queue import Queue
from threading import Thread

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

size = (1080, 1380)

info_height = 100
button_height = 200


def full_solve_queue(q, cells, num_stars):
    q.put(full_solution(cells, num_stars))


def draw_board(screen, cells, marked_cells, show_solution, solution, delta_x, delta_y):
    screen.fill(WHITE)
    sysfont = pygame.font.get_default_font()
    plus_font = pygame.font.SysFont(sysfont, round(size[0]/7))
    mark = plus_font.render("+", True, BLACK)
    start_y = info_height
    for y, row in enumerate(cells):
        start_x = 0
        for x, cell in enumerate(row):
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


def loop(cells, num_stars):

    q = Queue()
    thread = Thread(target=full_solve_queue, args=(q, cells, num_stars))
    thread.start()
    pygame.init()
    screen = pygame.display.set_mode(size)
    width = len(cells)

    marked_cells = [[0]*width for _ in range(width)]
    solution = [[0]*width for _ in range(width)]

    # Define some colors

    delta_x = size[0] / width
    delta_y = (size[1] - button_height - info_height) / width
    # The loop will carry on until the user exit the game (e.g. clicks the close button).
    carry_on = True
    sysfont = pygame.font.get_default_font()
    font = pygame.font.SysFont(sysfont, round(size[0]/22.5))
    show_solution = False
    # The clock will be used to control how fast the screen updates
    clock = pygame.time.Clock()
    if num_stars == 1:
        status = "You need {} star per block, row and column".format(num_stars)
    else:
        status = "You need {} stars per block, row and column".format(
            num_stars)
    info_text = font.render(status, True, BLACK)
    info_rect = info_text.get_rect(center=(size[0]/2, info_height / 2))
    error_text = font.render("", True, BLACK)
    solution = []
    valid = False
    while carry_on:
        # --- Main event loop
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                carry_on = False  # Flag that we are done so we exit this loop
            if event.type == pygame.MOUSEBUTTONDOWN:
                if mouse[1] < size[1] - button_height and mouse[1] > info_height:
                    cell_y = int((mouse[1] - info_height) / delta_y)
                    cell_x = int(mouse[0] / delta_x)

                    marked_cells[cell_y][cell_x] = 0 if marked_cells[cell_y][cell_x] == 1 else 1
                valid, error = verify_solution(num_stars, cells, marked_cells)
                if valid:
                    carry_on = False
                else:
                    error_text = font.render(error, True, BLACK)
        if q.qsize() > 0:
            solution = q.get()
            show_solution = True
            print("solution available, it's", solution)

        draw_board(screen, cells, marked_cells,
                   show_solution, solution, delta_x, delta_y)
        text_rect = error_text.get_rect(
            center=(size[0]/2, size[1]-(button_height/2)))
        screen.blit(error_text, text_rect)
        pygame.draw.line(screen, BLACK, [0, info_height], [
                         size[0], info_height])
        screen.blit(info_text, info_rect)
        pygame.draw.rect(
            screen, BLACK, [0, size[1]-button_height, size[0], size[1]], width=3)
        pygame.display.flip()

        # --- Limit to 60 frames per second
        clock.tick(60)
    if valid:
        font = pygame.font.SysFont(sysfont, round(size[0]/11))
        win_text = font.render("You WON!", True, BLACK)
        text_rect = win_text.get_rect(center=(size[0] / 2, size[1] / 2))
        screen.blit(win_text, text_rect)
        pygame.display.flip()
        time.sleep(4)
    # Once we have exited the main program loop we can stop the game engine:
    pygame.quit()
