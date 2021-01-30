import pygame


def loop(cells):
    pygame.init()
    size = (1080, 1280)
    screen = pygame.display.set_mode(size)
    width = len(cells)

    marked_cells = [[0]*width for _ in range(width)]
    # Define some colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)

    button_height = 200

    delta_x = size[0] / width
    delta_y = (size[1] - button_height) / width
    # The loop will carry on until the user exit the game (e.g. clicks the close button).
    carryOn = True
    sysfont = pygame.font.get_default_font()
    font = pygame.font.SysFont(sysfont, 48)
    # The clock will be used to control how fast the screen updates
    clock = pygame.time.Clock()

    # -------- Main Program Loop -----------
    while carryOn:
        # --- Main event loop
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                carryOn = False  # Flag that we are done so we exit this loop
            if event.type == pygame.MOUSEBUTTONDOWN:
                if mouse[1] > size[1] - button_height:
                    pass
                else:
                    marked_cells[int(mouse[1] / delta_y)][int(mouse[0] /
                                                              delta_x)] = (marked_cells[int(mouse[1] / delta_y)][int(mouse[0] / delta_x)] + 1) % 2
        screen.fill(WHITE)
        start_y = 0
        for y, row in enumerate(cells):
            start_x = 0
            for x, cell in enumerate(row):
                if marked_cells[y][x] == 1:
                    pygame.draw.rect(screen, YELLOW, [
                                     start_x, start_y, delta_x, delta_y])
                else:
                    pygame.draw.rect(screen, WHITE, [
                                     start_x, start_y, delta_x, delta_y])
                if y >= 1:
                    if cells[y - 1][x] == cells[y][x]:
                        pygame.draw.line(screen, BLACK, [start_x, start_y], [
                                         start_x + delta_x, start_y], 1)
                    else:
                        pygame.draw.line(screen, BLACK, [start_x, start_y], [
                                         start_x+delta_x, start_y], 5)
                if x >= 1:
                    if cells[y][x-1] == cells[y][x]:
                        pygame.draw.line(screen, BLACK, [start_x, start_y], [
                                         start_x, start_y+delta_y], 1)
                    else:
                        pygame.draw.line(screen, BLACK, [start_x, start_y], [
                                         start_x, start_y+delta_y], 5)
                start_x += delta_x

            start_y += delta_y
        text = font.render("Validate solution", True, BLACK)
        text_rect = text.get_rect(
            center=(size[0]/2, size[1]-(button_height/2)))
        screen.blit(text, text_rect)

        pygame.draw.rect(
            screen, BLACK, [0, size[1]-button_height, size[0], size[1]], width=3)
        pygame.display.flip()

        # --- Limit to 60 frames per second
        clock.tick(60)

    # Once we have exited the main program loop we can stop the game engine:
    pygame.quit()