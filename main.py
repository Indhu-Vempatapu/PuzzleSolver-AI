import pygame
import numpy as np
import time
import asyncio
import algorithm as puzzle_solver

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 0, 0
FPS = 60
FONT = pygame.font.SysFont("Comic Sans MS", 26, bold=True)
SMALL_FONT = pygame.font.SysFont("Courier New", 20, bold=True)

TILE_SIZE = 60
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 40

# Colors
from pygame import Color
PASTEL_RED = Color(255, 204, 203)
PASTEL_BLUE = Color(174, 198, 207)
PASTEL_GREEN = Color(204, 255, 229)
PASTEL_PURPLE = Color(229, 204, 255)

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
LIGHT_GRAY = (224, 224, 224)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
GREEN = (76, 175, 80)
RED = (244, 67, 54)
ORANGE = (255, 152, 0)
PURPLE = (123, 104, 238)
BLUE = (33, 150, 243)
LIGHT_BLUE = (173, 216, 230)
TEAL = (0, 128, 128)

class RadioButton:
    def __init__(self, x, y, text, value):
        self.rect = pygame.Rect(x, y, 30, 30)  
        self.text = text
        self.value = value
        self.selected = False

    def draw(self, screen):
        center = (self.rect.centerx, self.rect.centery)
        pygame.draw.circle(screen, BLACK, center, 12, 2)
        if self.selected:
            pygame.draw.circle(screen, BLUE, center, 6)
        text_surface = SMALL_FONT.render(self.text, True, BLACK)
        screen.blit(text_surface, (self.rect.x + 40, self.rect.y + 5))

    def handle_event(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            return self.value
        return None

class ScrollablePanel:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.virtual_height = 0
        self.virtual_surface = None
        self.offset_y = 0
        self.scrollbar_rect = pygame.Rect(x + width - 20, y, 20, height)
        self.scrollbar_handle = pygame.Rect(x + width - 20, y, 20, 0)
        self.radio_buttons = []
        self.labels = []
        self.dragging_scrollbar = False

    def add_radio_button(self, x, y, text, value):
        button = RadioButton(x, y, text, value)
        self.radio_buttons.append(button)
        self.virtual_height = max(self.virtual_height, y + 40)

    def add_label(self, x, y, text):
        self.labels.append((x, y, text))
        self.virtual_height = max(self.virtual_height, y + 40)

    def update_scrollbar(self):
        if self.virtual_height <= self.rect.height:
            self.scrollbar_handle.height = self.scrollbar_rect.height
            self.offset_y = 0
        else:
            handle_ratio = self.rect.height / self.virtual_height
            self.scrollbar_handle.height = max(20, self.scrollbar_rect.height * handle_ratio)
            max_offset = self.virtual_height - self.rect.height
            self.offset_y = min(max(0, self.offset_y), max_offset)
            handle_y = self.scrollbar_rect.y + (self.offset_y / max_offset) * (self.scrollbar_rect.height - self.scrollbar_handle.height)
            self.scrollbar_handle.y = handle_y

    def draw(self, screen):
        if not self.virtual_surface or self.virtual_surface.get_height() != self.virtual_height:
            self.virtual_surface = pygame.Surface((self.rect.width, self.virtual_height))
        self.virtual_surface.fill(LIGHT_GRAY)
        for x, y, text in self.labels:
            label_surface = SMALL_FONT.render(text, True, BLACK)
            self.virtual_surface.blit(label_surface, (x, y))
        for button in self.radio_buttons:
            button.draw(self.virtual_surface)
        screen.set_clip(self.rect)
        screen.blit(self.virtual_surface, (self.rect.x, self.rect.y - self.offset_y))
        screen.set_clip(None)
        if self.virtual_height > self.rect.height:
            pygame.draw.rect(screen, GRAY, self.scrollbar_rect)
            pygame.draw.rect(screen, DARK_GRAY, self.scrollbar_handle)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            mouse_x, mouse_y = event.pos
            virtual_mouse_y = mouse_y + self.offset_y - self.rect.y
            for button in self.radio_buttons:
                value = button.handle_event((mouse_x - self.rect.x, virtual_mouse_y))
                if value:
                    for b in self.radio_buttons:
                        b.selected = (b.value == value)
                    return value
        if event.type == pygame.MOUSEBUTTONDOWN and self.scrollbar_rect.collidepoint(event.pos):
            if self.scrollbar_handle.collidepoint(event.pos):
                self.dragging_scrollbar = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_scrollbar = False
        elif event.type == pygame.MOUSEMOTION and self.dragging_scrollbar:
            max_offset = self.virtual_height - self.rect.height
            dy = event.rel[1] * (self.virtual_height / (self.scrollbar_rect.height - self.scrollbar_handle.height))
            self.offset_y = min(max(0, self.offset_y + dy), max_offset)
            self.update_scrollbar()
        if event.type == pygame.MOUSEWHEEL and self.rect.collidepoint(pygame.mouse.get_pos()):
            self.offset_y = min(max(0, self.offset_y - event.y * 30), self.virtual_height - self.rect.height)
            self.update_scrollbar()
        return None

class Button:
    def __init__(self, x, y, w, h, text, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.enabled = True

    def draw(self, screen):
        color = self.color if self.enabled else GRAY
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)
        text_surface = FONT.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


    def handle_event(self, event):
        if self.enabled and event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            return self.text
        return None

class PuzzleApp:
    def __init__(self):
        info = pygame.display.Info()
        global WIDTH, HEIGHT
        WIDTH, HEIGHT = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)



        pygame.display.set_caption("8-Puzzle Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.start_time = None
        self.computation_time = 0.0
        self.auto_solve = False
        self.step_index = 0
        self.solution_step_index = 0
        self.solution_steps = []
        self.goal_state = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        self.start_board = np.array([[2, 6, 5], [0, 8, 7], [4, 3, 1]])
        self.goal_board = self.goal_state.copy()
        self.solution_board = np.zeros((3, 3), dtype=int)
        self.auto_board = np.zeros((3, 3), dtype=int)
        self.feedback_timer = 0

        # Algorithm configuration
        self.algorithms = {
            "bfs": {"func": puzzle_solver.bfs, "display": "BFS", "group": "Uninformed Search"},
            "dfs": {"func": puzzle_solver.dfs, "display": "DFS", "group": "Uninformed Search"},
            "ucs": {"func": puzzle_solver.ucs, "display": "UCS", "group": "Uninformed Search"},
            "ids": {"func": puzzle_solver.ids, "display": "IDS", "group": "Uninformed Search"},
            "a_star": {"func": puzzle_solver.a_star, "display": "A*", "group": "Informed Search"},
            "ida_star": {"func": puzzle_solver.ida_star, "display": "IDA*", "group": "Informed Search"},
            "gbfs": {"func": puzzle_solver.gs, "display": "Greedy", "group": "Informed Search"},
            
        }

        # Scrollable panel
        self.algorithm = "bfs"
        self.panel = ScrollablePanel(int(WIDTH * 0.75), int(HEIGHT * 0.05), 300, int(HEIGHT * 0.8))

        y_pos = 20
        current_group = ""
        for algo_key, algo_info in self.algorithms.items():
            group = algo_info["group"]
            if group != current_group:
                self.panel.add_label(10, y_pos, group)
                y_pos += 40
                current_group = group
            self.panel.add_radio_button(10, y_pos, algo_info["display"], algo_key)
            if algo_key == "bfs":
                self.panel.radio_buttons[-1].selected = True
            y_pos += 40
        self.panel.update_scrollbar()

        # Buttons
        self.auto_button = Button(150, 250, BUTTON_WIDTH, BUTTON_HEIGHT, "SOLVE", ORANGE)
        self.auto_button.enabled = True
        self.reset_button = Button(350, 250, BUTTON_WIDTH, BUTTON_HEIGHT, "RESET", RED)
        self.exit_button = Button(WIDTH // 2 + 150, 250, BUTTON_WIDTH, BUTTON_HEIGHT, "EXIT", DARK_GRAY)

        self.prev_button = Button(80, 550, BUTTON_WIDTH, BUTTON_HEIGHT, "PREVIOUS", TEAL)
        self.prev_button.enabled = False
        self.next_button = Button(420, 550, BUTTON_WIDTH, BUTTON_HEIGHT, "NEXT", BLUE)
        self.next_button.enabled = False

        # Result text
        self.result_text = ""
        self.result_text_steps = ""
        self.result_text_time = ""

    def reset(self):
        self.step_index = 0
        self.solution_step_index = 0
        self.solution_steps = []
        self.result_text = ""
        self.result_text_steps = ""
        self.result_text_time = ""
        self.start_board = np.array([[2, 6, 5], [0, 8, 7], [4, 3, 1]])
        self.goal_board = self.goal_state.copy()
        self.solution_board = np.zeros((3, 3), dtype=int)
        self.auto_board = np.zeros((3, 3), dtype=int)
        self.auto_button.enabled = True
        self.auto_button.text = "SOLVE"
        self.auto_solve = False
        self.computation_time = 0.0
        self.next_button.enabled = False
        self.prev_button.enabled = False
        self.feedback_timer = 0

    def update_timer(self):
        if self.computation_time > 0:
            return f"Time: {self.computation_time:.2f} second"
        return ""

    def solve(self):
        self.step_index = 0
        self.solution_step_index = 0
        self.solution_steps = []
        self.result_text = "Finding solution..."
        self.result_text_steps = ""
        self.result_text_time = ""
        self.solution_board = np.zeros((3, 3), dtype=int)
        self.auto_board = np.zeros((3, 3), dtype=int)
        self.next_button.enabled = False
        self.prev_button.enabled = False
        self.computation_time = 0.0
        self.feedback_timer = 0

        self.draw()
        pygame.display.flip()

        start = self.start_board.copy()
        self.goal_state = self.goal_board.copy()

        self.start_time = time.time()

        solver_func = self.algorithms[self.algorithm]["func"]
        result = solver_func(start, self.goal_state)

        if result is not None and not isinstance(result, list):
            result = [result]
        self.solution_steps = result if result is not None else []

        self.computation_time = time.time() - self.start_time

        if self.solution_steps:
            self.result_text = ""
            self.result_text_steps = f"Number of steps: {len(self.solution_steps) - 1}"
            self.result_text_time = f"Time: {self.computation_time:.2f} second"
            self.auto_button.enabled = True
            self.auto_button.text = "STOP"
            self.auto_solve = True
            self.next_button.enabled = len(self.solution_steps) > 1
            self.prev_button.enabled = False
            self.solution_step_index = 0
            self.solution_board = self.solution_steps[0]
            self.auto_board = self.solution_steps[0]
        else:
            self.result_text = "No solution found!" if self.algorithm != "pg" else "Policy-gradient not implemented!"
            self.result_text_steps = ""
            self.result_text_time = ""
            self.auto_button.text = "SOLVE"
            self.auto_solve = False

        self.draw()
        pygame.display.flip()

    def show_step(self):
        if self.step_index < len(self.solution_steps):
            self.auto_board = self.solution_steps[self.step_index]
            self.step_index += 1
            if np.array_equal(self.auto_board, self.goal_state):
                self.auto_button.text = "SOLVE"
                self.auto_button.enabled = True
                self.auto_solve = False
            return True
        else:
            self.auto_button.enabled = True
            self.auto_button.text = "SOLVE"
            self.auto_solve = False
            return False

    def next_step(self):
        if self.solution_step_index < len(self.solution_steps) - 1:
            self.solution_step_index += 1
            self.solution_board = self.solution_steps[self.solution_step_index]
            self.prev_button.enabled = self.solution_step_index > 0
            self.next_button.enabled = self.solution_step_index < len(self.solution_steps) - 1

    def previous_step(self):
        if self.solution_step_index > 0:
            self.solution_step_index -= 1
            self.solution_board = self.solution_steps[self.solution_step_index]
            self.next_button.enabled = True
            self.prev_button.enabled = self.solution_step_index > 0

    def toggle_auto_solve(self):
        self.auto_solve = not self.auto_solve
        if self.auto_solve:
            self.auto_button.text = "STOP"
            if self.step_index < len(self.solution_steps):
                self.auto_board = self.solution_steps[self.step_index]
        else:
            self.auto_button.text = "SOLVE"

    def draw_board(self, board, x_offset, y_offset, bg_color):
        for i in range(3):
            for j in range(3):
                x = x_offset + j * TILE_SIZE
                y = y_offset + i * TILE_SIZE
                value = board[i][j]
                color = bg_color if value != 0 else GRAY
                pygame.draw.rect(self.screen, color, (x, y, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(self.screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE), 2)
                if value != 0:
                    text = FONT.render(str(value), True, BLACK)
                    text_rect = text.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
                    self.screen.blit(text, text_rect)

    def draw(self):

        self.screen.fill((240, 248, 255))  
        self.screen.blit(SMALL_FONT.render("INITIAL STATE", True, BLACK), (WIDTH // 5 + 20, HEIGHT // 10 - 30))
        self.screen.blit(SMALL_FONT.render("FINAL STATE", True, BLACK), (WIDTH // 2 + 20, HEIGHT // 10 - 30))
        self.screen.blit(SMALL_FONT.render("Details", True, BLACK), (WIDTH // 5 + 20, HEIGHT // 2 - 30))
        self.screen.blit(SMALL_FONT.render("Auto Solve", True, BLACK), (WIDTH // 2 + 20, HEIGHT // 2 - 30))
        self.draw_board(self.start_board, WIDTH // 5, HEIGHT // 10, PASTEL_GREEN)
        self.draw_board(self.goal_board, WIDTH // 2, HEIGHT // 10, PASTEL_PURPLE)
        self.draw_board(self.solution_board, WIDTH // 5, HEIGHT // 2, PASTEL_BLUE)
        self.draw_board(self.auto_board, WIDTH // 2, HEIGHT // 2, PASTEL_RED)
        
        button_y = HEIGHT // 2 + TILE_SIZE * 3 + 40  
        button_spacing = 20
        total_width = BUTTON_WIDTH * 4 + button_spacing * 3
        start_x = (WIDTH // 5 + WIDTH // 2 + TILE_SIZE * 3) // 2 - total_width // 2

        self.prev_button = Button(start_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "PREVIOUS", TEAL)
        self.auto_button = Button(start_x + (BUTTON_WIDTH + button_spacing), button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "SOLVE", ORANGE)
        self.reset_button = Button(start_x + 2 * (BUTTON_WIDTH + button_spacing), button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "RESET", RED)
        self.next_button = Button(start_x + 3 * (BUTTON_WIDTH + button_spacing), button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "NEXT", BLUE)



        if self.solution_steps and np.any(self.solution_board):
            step_text = f"Step {self.solution_step_index}/{len(self.solution_steps) - 1}"
            step_label = SMALL_FONT.render(step_text, True, BLACK)
            self.screen.blit(step_label, (125, 520))

        self.panel.draw(self.screen)
        self.panel.rect.y = int((HEIGHT - self.panel.rect.height) // 2)
        self.panel.update_scrollbar()
        self.auto_button.draw(self.screen)
        self.reset_button.draw(self.screen)
        self.prev_button.draw(self.screen)
        self.next_button.draw(self.screen)
        
        if self.panel.radio_buttons:
            last_button = self.panel.radio_buttons[-1]
            status_x = self.panel.rect.x + 10
            status_y = self.panel.rect.y + last_button.rect.bottom + 30 

            if self.result_text:
                friendly_msg = self.result_text.replace("Finding solution...", "Solving puzzle... please wait...")
                self.screen.blit(SMALL_FONT.render(friendly_msg, True, BLACK), (status_x, status_y))

            if self.result_text_steps:
                self.screen.blit(SMALL_FONT.render(self.result_text_steps, True, BLACK), (status_x, status_y + 25))

            if self.result_text_time:
                self.screen.blit(SMALL_FONT.render(self.result_text_time, True, BLACK), (status_x, status_y + 50))


            

        pygame.display.flip()

    async def update_loop(self):
        if self.auto_solve:
            if self.show_step():
                await asyncio.sleep(1.0)
            else:
                self.toggle_auto_solve()

    def setup(self):
        pass

    async def main(self):
        self.setup()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False

                value = self.panel.handle_event(event)
                if value:
                    print(f"Selected algorithm: {self.algorithms[value]['display']} ({value})")
                    self.algorithm = value
                    for button in self.panel.radio_buttons:
                        button.selected = (button.value == value)
                    self.feedback_timer = time.time() + 2
                    self.draw()
                    pygame.display.flip()
                if self.auto_button.handle_event(event) in ["SOLVE", "STOP"]:
                    if self.auto_button.text == "SOLVE":
                        if not self.solution_steps:
                            self.solve()
                        else:
                            self.toggle_auto_solve()
                    else:
                        self.toggle_auto_solve()
                if self.reset_button.handle_event(event) == "RESET":
                    self.reset()
                if self.exit_button.handle_event(event) == "EXIT":
                    self.running = False

                if self.next_button.handle_event(event) == "NEXT":
                    self.next_step()
                if self.prev_button.handle_event(event) == "PREVIOUS":
                    self.previous_step()
            await self.update_loop()
            self.draw()
            await asyncio.sleep(1.0 / FPS)

if __name__ == "__main__":
    app = PuzzleApp()
    asyncio.run(app.main())
