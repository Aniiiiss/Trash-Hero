import pygame
from src.settings import WIDTH, HEIGHT, WHITE, BLACK, GREEN, BLUE

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.SysFont("arial", 64, bold=True)
        self.button_font = pygame.font.SysFont("arial", 36)

        # Rectangle du bouton "Jouer"
        self.play_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 60)

    def draw(self):
        self.screen.fill(WHITE)

        # Titre
        title_text = self.title_font.render("Trash Hero", True, GREEN)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.screen.blit(title_text, title_rect)

        # Bouton jouer
        pygame.draw.rect(self.screen, BLUE, self.play_button, border_radius=12)
        button_text = self.button_font.render("Jouer", True, WHITE)
        button_rect = button_text.get_rect(center=self.play_button.center)
        self.screen.blit(button_text, button_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.play_button.collidepoint(event.pos):
                return "play"

        return None