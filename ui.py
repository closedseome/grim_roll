import pygame
from engine import BattleEngine

# =====================================================================
# НАСТРОЙКИ СТИЛЯ (3-й разработчик может менять палитру и размеры здесь)
# =====================================================================
BG_COLOR = (25, 25, 35)
CARD_COLOR = (45, 50, 65)
CARD_HOVER = (65, 72, 95)
DICE_COLOR = (230, 230, 235)
DICE_SELECTED = (255, 200, 50)
TEXT_COLOR = (240, 240, 240)
ACCENT_RED = (200, 60, 60)
ACCENT_BLUE = (60, 140, 220)
BTN_COLOR = (70, 160, 90)


class GraphicalUI:
    def __init__(self, width: int = 900, height: int = 600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("GRIM ROLL")
        
        self.font_large = pygame.font.SysFont("arial", 28, bold=True)
        self.font_med = pygame.font.SysFont("arial", 20)
        self.font_small = pygame.font.SysFont("arial", 15)

        # Прямоугольники для отслеживания кликов
        self.dice_rects = []
        self.card_rects = []
        self.end_turn_rect = pygame.Rect(width - 200, height - 70, 170, 45)

    def draw(self, engine: BattleEngine):
        self.screen.fill(BG_COLOR)
        mouse_pos = pygame.mouse.get_pos()

        # 1. Верхняя панель (Статус и прогресс)
        stage_text = self.font_med.render(
            f"Этап: {engine.current_enemy_idx + 1} / {len(engine.enemies)}", True, TEXT_COLOR
        )
        self.screen.blit(stage_text, (30, 20))

        msg_text = self.font_med.render(engine.status_message, True, DICE_SELECTED)
        self.screen.blit(msg_text, (220, 20))

        # 2. Персонажи (Игрок слева, Враг справа)
        self._draw_entity(engine.player, x=80, y=90, color=ACCENT_BLUE)
        self._draw_entity(engine.enemy, x=570, y=90, color=ACCENT_RED)

        # 3. Кубики по центру
        self.dice_rects.clear()
        start_dice_x = (self.width - (len(engine.dice_pool) * 80)) // 2
        for i, val in enumerate(engine.dice_pool):
            rect = pygame.Rect(start_dice_x + i * 80, 230, 60, 60)
            self.dice_rects.append(rect)
            
            color = DICE_SELECTED if i == engine.selected_dice_idx else DICE_COLOR
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            
            val_surf = self.font_large.render(str(val), True, (20, 20, 20))
            val_rect = val_surf.get_rect(center=rect.center)
            self.screen.blit(val_surf, val_rect)

        # 4. Карты игрока внизу экрана
        self.card_rects.clear()
        card_w, card_h = 200, 180
        spacing = 25
        total_w = len(engine.player.deck) * (card_w + spacing) - spacing
        start_card_x = (self.width - total_w) // 2

        for i, card in enumerate(engine.player.deck):
            rect = pygame.Rect(start_card_x + i * (card_w + spacing), 330, card_w, card_h)
            self.card_rects.append(rect)
            
            color = CARD_HOVER if rect.collidepoint(mouse_pos) else CARD_COLOR
            pygame.draw.rect(self.screen, color, rect, border_radius=12)
            pygame.draw.rect(self.screen, (100, 110, 140), rect, width=2, border_radius=12)

            # Текст внутри карты
            name_surf = self.font_med.render(card.name, True, TEXT_COLOR)
            cond_surf = self.font_small.render(f"[{card.condition_desc}]", True, DICE_SELECTED)
            self.screen.blit(name_surf, (rect.x + 12, rect.y + 15))
            self.screen.blit(cond_surf, (rect.x + 12, rect.y + 45))
            
            self._draw_wrapped_text(card.description, rect.x + 12, rect.y + 75, card_w - 24)

        # 5. Кнопка "Закончить ход"
        pygame.draw.rect(self.screen, BTN_COLOR, self.end_turn_rect, border_radius=8)
        btn_text = self.font_med.render("Конец хода", True, TEXT_COLOR)
        self.screen.blit(btn_text, btn_text.get_rect(center=self.end_turn_rect.center))

        pygame.display.flip()

    def _draw_entity(self, entity, x: int, y: int, color: tuple):
        """Отрисовка карточки персонажа (место для спрайтов 3-го разработчика)."""
        box = pygame.Rect(x, y, 250, 110)
        pygame.draw.rect(self.screen, (38, 40, 52), box, border_radius=10)
        pygame.draw.rect(self.screen, color, box, width=2, border_radius=10)

        name = self.font_med.render(entity.name, True, TEXT_COLOR)
        hp = self.font_med.render(f"HP: {entity.hp} / {entity.max_hp}", True, color)
        block = self.font_small.render(f"Броня: {entity.block}", True, (180, 200, 255))

        self.screen.blit(name, (x + 15, y + 12))
        self.screen.blit(hp, (x + 15, y + 45))
        self.screen.blit(block, (x + 15, y + 75))

    def _draw_wrapped_text(self, text: str, x: int, y: int, max_width: int):
        """Перенос длинного описания карты по словам."""
        words = text.split(" ")
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if self.font_small.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)

        for i, line in enumerate(lines):
            surf = self.font_small.render(line, True, (200, 200, 210))
            self.screen.blit(surf, (x, y + i * 18))

    def handle_click(self, pos: tuple[int, int], engine: BattleEngine):
        """Передача кликов мыши в движок."""
        for i, rect in enumerate(self.dice_rects):
            if rect.collidepoint(pos):
                engine.select_dice(i)
                return

        for i, rect in enumerate(self.card_rects):
            if rect.collidepoint(pos):
                engine.try_play_card(i)
                return

        if self.end_turn_rect.collidepoint(pos):
            engine.end_player_turn()
