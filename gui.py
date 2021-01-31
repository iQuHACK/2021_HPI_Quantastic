import pygame
import time
from starbattle import full_solution, verify_solution
from queue import Queue
from threading import Thread

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 200, 0)
GREY = (200, 200, 200)
RED = (255, 17,0)

# Define the size of the Player window
size = [500, 500]

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
    screen.fill(WHITE)
    sysfont = pygame.font.get_default_font()
    plus_font = pygame.font.SysFont(sysfont, round(size[1]/7))
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

def draw_results(screen, user_time, qpu_time, valid, found_solution):
    font_size = round(size[1]/20)
    sysfont = pygame.font.get_default_font()
    font = pygame.font.SysFont(sysfont, font_size)

    if found_solution:
        qpu_text = font.render("QPU time: " + qpu_time + "s", True, BLACK)
    else:
        qpu_text = font.render("QPU didn't finish", True, BLACK)

    if valid:
        pygame.draw.rect(
           screen, WHITE, [size[0]/4, size[1]/2 - 1.5 * font_size, size[0]/2, font_size*3])
        pygame.draw.rect(
           screen, BLACK, [size[0]/4, size[1]/2 - 1.5 * font_size, size[0]/2, font_size*3], 5)
        your_text = font.render("Your time: " + user_time + "s", True, BLACK)
        text_rect_your_time = your_text.get_rect(center=(size[0] / 2, size[1] / 2 ))
        screen.blit(your_text, text_rect_your_time)

        text_rect_qpu_time = qpu_text.get_rect(center=(size[0] / 2, size[1] / 2 + font_size))
        screen.blit(qpu_text, text_rect_qpu_time)
        result_text = "You WON!"
        win_text = font.render(result_text, True, BLACK)

        text_rect_you_won = win_text.get_rect(center=(size[0] / 2, size[1] / 2 + -1 * font_size))
        screen.blit(win_text, text_rect_you_won)
        pygame.display.flip()
    else:
        draw_button(screen, GREY)
        text_rect = qpu_text.get_rect(
        center=(size[0]/4*3, size[1]-(button_height/2)))
        screen.blit(qpu_text, text_rect)
        pygame.display.flip()

def draw_button(screen, button_color):
    pygame.draw.rect(
        screen, button_color, [size[0]/2, size[1]-button_height, size[0]/2, button_height])


def loop(cells, num_stars):
    """ This loop draws a gui, specified by cells and num_stars
    cells: The original cells with the information about the blocks
    num_stars: The number of stars the player has to mark in every block, column and row
    """
    
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
    carry_on = True
    sysfont = pygame.font.get_default_font()
    font = pygame.font.SysFont(sysfont, round(size[1]/22.5))
    found_solution = False
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
    qpu_valid = False
    valid = False
    running = True
    while carry_on:
        # --- Main event loop
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                carry_on = False  # Flag that we are done so we exit this loop
            if event.type == pygame.MOUSEBUTTONDOWN:
                if mouse[1] < size[1] - button_height and mouse[1] > info_height and running:
                    cell_y = int((mouse[1] - info_height) / delta_y)
                    cell_x = int(mouse[0] / delta_x)

                    marked_cells[cell_y][cell_x] = 0 if marked_cells[cell_y][cell_x] == 1 else 1
                valid, error = verify_solution(num_stars, cells, marked_cells)
                if valid and running:
                    running = False
                    user_end = time.time()
                else:
                    error_text = font.render(error, True, BLACK)
                if mouse[0] >= size[0]/2 and mouse[1] >= size[1]-button_height and found_solution:
                    show_solution = True
            

        if q.qsize() > 0:
            solution = q.get()
            found_solution = True
            qpu_valid, _ = verify_solution(num_stars, cells, solution)
            qpu_end = time.time()
            print("solution available, it's", solution)


        draw_board(screen, cells, marked_cells,
                   show_solution, solution, delta_x, delta_y)
        text_rect = error_text.get_rect(
            center=(size[0]/4, size[1]-(button_height/2)))
        screen.blit(error_text, text_rect)
        pygame.draw.line(screen, BLACK, [0, info_height], [
                         size[0], info_height])
        screen.blit(info_text, info_rect)


        button_color = GREY
        if mouse[0] >= size[0]/2 and mouse[1] >= size[1]-button_height and found_solution and qpu_valid:
            button_color = GREEN
        elif found_solution and qpu_valid:
            button_color = DARKGREEN
        elif found_solution:
            button_color = RED   
        draw_button(screen, button_color)

        solution_text = ""
        if found_solution and qpu_valid:
            solution_text = font.render("Show Solution", True, BLACK)
        elif found_solution:
            solution_text = font.render("QPU failed", True, BLACK)
        else:
            solution_text = font.render("QPU is running", True, BLACK)

        text_rect = solution_text.get_rect(
            center=(size[0]/4*3, size[1]-(button_height/2)))
        screen.blit(solution_text, text_rect)

        pygame.draw.rect(
            screen, BLACK, [0, size[1]-button_height, size[0], size[1]], width=3)        

        if show_solution or valid:
            draw_results(screen, str(round(user_end - start, 2)), str(round(qpu_end - start, 2)),valid, found_solution)
        pygame.display.flip()

        # --- Limit to 60 frames per second
        clock.tick(60)

    
    
    
    # Once we have exited the main program loop we can stop the game engine:
    pygame.quit()
