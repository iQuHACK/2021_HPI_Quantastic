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
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)

    button_height = 200

    width_offset = size[0] / width
    height_offset = (size[1] - button_height) / width
    # Define some colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    # The loop will carry on until the user exit the game (e.g. clicks the close button).
    carryOn = True

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
                    marked_cells[int(mouse[1] / height_offset)][int(mouse[0] /
                                                                    width_offset)] = (marked_cells[int(mouse[1] / height_offset)][int(mouse[0] / width_offset)] + 1) % 2
        screen.fill(WHITE)
        draw_height = 0
        for y, row in enumerate(cells):
            draw_width = 0
            for x, cell in enumerate(row):
                if marked_cells[y][x] == 1:
                    pygame.draw.rect(screen, RED, [
                                     draw_width, draw_height, width_offset, height_offset])
                else:
                    pygame.draw.rect(screen, WHITE, [
                                     draw_width, draw_height, width_offset, height_offset])
                if y >= 1:
                    if cells[y - 1][x] == cells[y][x]:
                        pygame.draw.line(screen, BLACK, [draw_width, draw_height], [
                                         draw_width + width_offset, draw_height], 1)
                    else:
                        pygame.draw.line(screen, BLACK, [draw_width, draw_height], [
                                         draw_width+width_offset, draw_height], 5)
                if x >= 1:
                    if cells[y][x-1] == cells[y][x]:
                        pygame.draw.line(screen, BLACK, [draw_width, draw_height], [
                                         draw_width, draw_height+height_offset], 1)
                    else:
                        pygame.draw.line(screen, BLACK, [draw_width, draw_height], [
                                         draw_width, draw_height+height_offset], 5)
                draw_width = draw_width+width_offset

            draw_height = draw_height + height_offset
        pygame.draw.rect(
            screen, BLACK, [0, size[1]-button_height, size[0], size[1]], width=3)
        pygame.display.flip()

        # --- Limit to 60 frames per second
        clock.tick(60)

    # Once we have exited the main program loop we can stop the game engine:
    pygame.quit()
