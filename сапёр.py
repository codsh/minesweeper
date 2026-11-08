import time
import random
import pygame

pygame.init()

last_bomb_explosion_time = 0
time_between_explosions = 3

multimedia = 'pictures and music'

flag_image = pygame.image.load(f'{multimedia}/flag_of_bomb.png')
bomb_image = pygame.image.load(f'{multimedia}/bomb.png')
minesweeper_icon = pygame.image.load(f'{multimedia}/minesweeper.ico')

game_start_sound = pygame.mixer.Sound(f'{multimedia}/start_the_game.mp3')
opening_cell_sound = pygame.mixer.Sound(f'{multimedia}/open_cell.mp3')
setting_flag_sound = pygame.mixer.Sound(f'{multimedia}/set_flag.mp3')
bomb_explosion_sound = pygame.mixer.Sound(f'{multimedia}/bomb_explosion.mp3')
winning_game_sound = pygame.mixer.Sound(f'{multimedia}/game_win.mp3')

minesweeper_font = pygame.font.SysFont('Arial', 16, 'Bold')
font_of_game_result = pygame.font.SysFont('Arial', 40)
font_of_game_level = pygame.font.SysFont('Arial', 40)

SCREEN_WIDTH, SCREEN_HEIGHT = 1250, 900
color_list = [(0, 0, 0), (0, 0, 191), (0, 127, 0), (255, 0, 0), (127, 127, 0),
              (191, 95, 0), (0, 127, 159), (127, 0, 127), (0, 0, 0)]


class Button:
    def __init__(self, rect, color):
        self.rect, self.color = rect, color


level_buttons = {'easy': Button(rect=(0, 3, 190, 44), color=(127, 255, 127)),
                 'normal': Button(rect=(0, 53, 190, 44), color=(255, 255, 127)),
                 'hard': Button(rect=(0, 103, 190, 44), color=(255, 191, 127)),
                 'extreme': Button(rect=(0, 153, 190, 44), color=(255, 127, 127))}

lose_label = font_of_game_result.render('Поражение!', True, 'Blue')
win_label = font_of_game_result.render('Победа!', True, 'Blue')
easy_level_label = font_of_game_level.render('Новичок!', True, (0, 223, 0))
normal_level_label = font_of_game_level.render('Любитель!', True, (223, 223, 0))
hard_level_label = font_of_game_level.render('Профи!', True, (223, 111, 0))
insane_level_label = font_of_game_level.render('Экстремал!', True, (223, 0, 0))


class Cell:
    X, Y = 200, 50
    WIDTH = 20

    def __init__(self, column, row, opened=False):
        global time_between_explosions
        time_between_explosions = 3
        self.opened = opened
        self.bombs_around = 0
        self.has_flag = False
        self.has_bomb = False
        self.column, self.row = column, row
        self.x_coord = self.X + self.WIDTH * column
        self.y_coord = self.Y + self.WIDTH * row


class MineField:
    def __init__(self, columns, rows, number_of_mines):
        if number_of_mines > columns * rows:
            raise ValueError('Too many mines for field of this size!')
        self.rows, self.columns = rows, columns
        self.minefield = [[Cell(column, row) for column in range(columns)] for row in range(rows)]
        self.amount_of_flags = number_of_mines
        self.opened_squares = 0
        self.opened_squares_to_win = columns * rows - number_of_mines
        self.win = self.lose = False

        game_start_sound.play()
        
        
    def generate_mines(self, mouse_position):
        unwanted_y_bomb_numbers, unwanted_x_bomb_numbers = None, None
        for i, square_row in enumerate(self.minefield):
            for j, square in enumerate(square_row):
                square_rect = pygame.Rect((square.x_coord, square.y_coord, square.WIDTH - 1, square.WIDTH - 1))
                if square_rect.collidepoint(mouse_position):
                    unwanted_y_bomb_numbers, unwanted_x_bomb_numbers = range(i - 2, i + 3), range(j - 2, j + 3)
            if unwanted_x_bomb_numbers:
                break
        else:
            return False
        
        number_of_bombs_created_on_minefield = 0
        while number_of_bombs_created_on_minefield < self.amount_of_flags:
            x_bomb_number, y_bomb_number = random.randrange(self.columns), random.randrange(self.rows)
            if not self.minefield[y_bomb_number][x_bomb_number].has_bomb and not (x_bomb_number in unwanted_x_bomb_numbers and y_bomb_number in unwanted_y_bomb_numbers):
                self.minefield[y_bomb_number][x_bomb_number].has_bomb = True
                number_of_bombs_created_on_minefield += 1

        self.squares_for_bombs = [square for square_row in self.minefield for square in square_row if square.has_bomb]
        for square in self.squares_for_bombs:
            for neighbour_column in range(square.column - 1, square.column + 2):
                if neighbour_column not in range(self.columns):
                    continue
                for neighbour_row in range(square.row - 1, square.row + 2):
                    if neighbour_row not in range(self.rows):
                        continue
                    if neighbour_column == square.column and neighbour_row == square.row:
                        continue
                    self.minefield[neighbour_row][neighbour_column].bombs_around += 1
                    
        return True
        

    def show_cells(self):
        if self.lose:
            screen.blit(lose_label, (600, 0))
        elif self.opened_squares == self.opened_squares_to_win:
            screen.blit(win_label, (600, 0))
            self.win = True
        for square_row in self.minefield:
            for square in square_row:
                if square.has_flag:
                    screen.blit(flag_image, (square.x_coord + 2, square.y_coord + 2))
                if square.has_bomb and self.win:
                    continue
                if not square.opened:
                    continue
                elif square.has_bomb:
                    if square.has_flag:
                        square.has_flag = False
                        minefield.amount_of_flags += 1
                    screen.blit(bomb_image, (square.x_coord + 1, square.y_coord + 1))
                elif square.bombs_around > 0:
                    pygame.draw.rect(screen, 'White',
                                     (square.x_coord, square.y_coord, square.WIDTH - 1, square.WIDTH - 1))
                    screen.blit(minesweeper_font.render(str(square.bombs_around), True, color_list[square.bombs_around]),
                                (square.x_coord + 5, square.y_coord))
                else:
                    pygame.draw.rect(screen, 'White',
                                     (square.x_coord, square.y_coord, square.WIDTH - 1, square.WIDTH - 1))
                    
    def open_cell(self, mouse_position, coord_list, crush_flags_on_the_way):
        if self.lose:
            bomb_index = random.randrange(len(self.squares_for_bombs))
            self.squares_for_bombs[bomb_index].opened = True
            self.squares_for_bombs.pop(bomb_index)
            bomb_explosion_sound.play()
            return False
        if (mouse_position[0], mouse_position[1]) in coord_list:
            return False
        coord_list.append(mouse_position)
        for square_row in self.minefield:
            for square in square_row:
                square_rect = pygame.Rect((square.x_coord, square.y_coord, square.WIDTH - 1, square.WIDTH - 1))
                if self.win or square.has_flag and (not crush_flags_on_the_way):
                    continue
                if self.lose and (not square.opened):
                    continue
                if square_rect.collidepoint(mouse_position):
                    if not square.opened:
                        square.opened = True
                        self.opened_squares += 1
                        if square.has_bomb:
                            bomb_explosion_sound.play()
                        elif self.opened_squares == self.opened_squares_to_win:
                            winning_game_sound.play()
                        else:
                            opening_cell_sound.play()

                    if square.has_flag and crush_flags_on_the_way:
                        square.has_flag = False
                        self.amount_of_flags += 1

                    if square.bombs_around == 0 and (not square.has_bomb):
                        return any([self.open_cell((mouse_position[0] + x_coord,
                                                    mouse_position[1] + y_coord), coord_list, True)
                                    for x_coord in [-square.WIDTH, 0, square.WIDTH]
                                    for y_coord in [-square.WIDTH, 0, square.WIDTH]
                                    if x_coord != 0 or y_coord != 0])

                    if square.has_bomb and (not self.lose):
                        return True
                    return False
        return False

    def set_flag(self):
        for square_row in self.minefield:
            for square in square_row:
                square_rect = pygame.Rect((square.x_coord, square.y_coord, square.WIDTH - 1, square.WIDTH - 1))
                if square.opened or (not square_rect.collidepoint(pygame.mouse.get_pos())):
                    continue
                if square.has_flag:
                    self.amount_of_flags += 1
                    square.has_flag = not square.has_flag
                    setting_flag_sound.play()
                elif not square.has_flag and self.amount_of_flags > 0:
                    self.amount_of_flags -= 1
                    square.has_flag = not square.has_flag
                    setting_flag_sound.play()


FPS = 50
timer = pygame.time.Clock()

close_the_game = False

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_icon(minesweeper_icon)
pygame.display.set_caption('Сапёр')

minefield = MineField(9, 9, 10)
level = 'easy'

while not close_the_game:
    screen.fill((207, 207, 207))

    if minefield.lose and minefield.squares_for_bombs:
        if time.time() - last_bomb_explosion_time > time_between_explosions:
            last_bomb_explosion_time = time.time()
            level_index = list(level_buttons.keys()).index(level)
            time_divide_by = (2, 3, 5, 16)[level_index]
            time_between_explosions = random.choice((0.2, 0.3, 0.5, 0.8, 1.3)) / time_divide_by
            minefield.open_cell(mouse_position=[], coord_list=[], crush_flags_on_the_way=None)

    the_mouse_position = pygame.mouse.get_pos()
    x, y = the_mouse_position
    for cell_row in minefield.minefield:
        for cell in cell_row:
            rgb_power = (127, 143, 175)[(cell.x_coord <= x <= cell.x_coord + cell.WIDTH - 1) + (cell.y_coord <= y <= cell.y_coord + cell.WIDTH - 1)]
            pygame.draw.rect(screen, (rgb_power, rgb_power, rgb_power), (cell.x_coord, cell.y_coord, cell.WIDTH - 1, cell.WIDTH - 1))
    minefield.show_cells()

    key = pygame.key.get_pressed()
    next_x, next_y = x + (key[pygame.K_RIGHT] - key[pygame.K_LEFT]) * Cell.WIDTH, y + (key[pygame.K_DOWN] - key[pygame.K_UP]) * Cell.WIDTH
    if next_x == x and next_y == y:
        next_x, next_y = x + (key[pygame.K_d] - key[pygame.K_a]) * Cell.WIDTH, y + (key[pygame.K_s] - key[pygame.K_w]) * Cell.WIDTH
    if (next_x != x or next_y != y) and (0 < next_x < SCREEN_WIDTH and 0 < next_y < SCREEN_HEIGHT):
        if mouse_pressed_cnt > FPS // 5 or mouse_pressed_cnt == 0:
            pygame.mouse.set_pos((next_x, next_y))
        mouse_pressed_cnt += 1
    else:
        mouse_pressed_cnt = 0
        next_x, next_y = x, y

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            close_the_game = True
        elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_f):
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_button = pygame.mouse.get_pressed()
            else:
                key = pygame.key.get_pressed()
                mouse_button = (any((key[pygame.K_RETURN], key[pygame.K_SPACE])), 'unknown', key[pygame.K_f])

            if mouse_button[2]:
                minefield.set_flag()

            if not mouse_button[0]:
                continue

            if (pygame.Rect(0, 3, 190, 44)).collidepoint(the_mouse_position):
                level = 'easy'
                minefield = MineField(9, 9, 10)
            if (pygame.Rect(0, 53, 190, 44)).collidepoint(the_mouse_position):
                level = 'normal'
                minefield = MineField(16, 16, 40)
            if (pygame.Rect(0, 103, 190, 44)).collidepoint(the_mouse_position):
                level = 'hard'
                minefield = MineField(30, 16, 99)
            if (pygame.Rect(0, 153, 190, 44)).collidepoint(the_mouse_position):
                level = 'extreme'
                minefield = MineField(50, 40, 400)

            if not hasattr(minefield, 'squares_for_bombs') and not minefield.generate_mines(the_mouse_position):
                minefield.open_cell(the_mouse_position, [], False)
                continue
            
            if minefield.squares_for_bombs and minefield.lose:
                continue

            if (not minefield.lose) and minefield.open_cell(pygame.mouse.get_pos(), [], False):
                minefield.lose = True
                last_bomb_explosion_time = time.time()

    if close_the_game:
        break

    for y_rect_coord in range(3, 200, 50):
        pygame.draw.rect(screen, (239, 239, 239), (0, y_rect_coord, 190, 44))

    pygame.draw.rect(screen, color=level_buttons[level].color, rect=level_buttons[level].rect)

    screen.blit(easy_level_label, (10, 0))
    screen.blit(normal_level_label, (10, 50))
    screen.blit(hard_level_label, (10, 100))
    screen.blit(insane_level_label, (10, 150))
    screen.blit(font_of_game_result.render(f'Количество флагов: {minefield.amount_of_flags}', True, 'Red'), (203, 0))

    pygame.display.update()

    timer.tick(FPS)
