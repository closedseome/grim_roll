import random
from entities import Player, Enemy

class DicePool:
    """Контейнер для кубиков, эмулирующий встроенный список."""

    def __init__(self):
        self._dice: list[int] = []

    def roll(self, count: int = 3) -> None:
        self._dice = [random.randint(1, 6) for _ in range(count)]

    def pop(self, index: int) -> int:
        return self._dice.pop(index)

    def is_empty(self) -> bool:
        return len(self._dice) == 0

    def __len__(self) -> int:
        return len(self._dice)

    def __getitem__(self, index: int) -> int:
        return self._dice[index]

    def __str__(self) -> str:
        return f"Кубики: {self._dice}"

    def __repr__(self) -> str:
        return f"DicePool({self._dice})"
class BattleEngine:
    def __init__(self, player: Player, enemies: list[Enemy]):
        self.player = player
        self.enemies = enemies
        self.current_enemy_idx = 0
        self.enemy = self.enemies[self.current_enemy_idx]
        
        self.dice_pool = DicePool()
        self._selected_dice_idx = None  # Индекс выбранного мышкой кубика
        self.status_message = "Ваш ход! Выберите кубик и карту."
        self._game_state = "PLAYING"    # PLAYING, VICTORY, GAME_OVER
        
        self.start_player_turn()

    @property
    def selected_dice_idx(self):
        return self._selected_dice_idx

    @selected_dice_idx.setter
    def selected_dice_idx(self, value):
        if value is None:
            self._selected_dice_idx = None
        elif 0 <= value < len(self.dice_pool):
            self._selected_dice_idx = value
        else:
            raise ValueError(
                f"Индекс {value} вне диапазона кубиков "
                f"(0-{len(self.dice_pool) - 1})"
            )

    @property
    def game_state(self) -> str:
        return self._game_state

    @game_state.setter
    def game_state(self, value: str):
        valid_states = {"PLAYING", "VICTORY", "GAME_OVER"}
        if value not in valid_states:
            raise ValueError(
                f"Недопустимое состояние: {value}. "
                f"Допустимы: {valid_states}"
            )
        self._game_state = value

    def start_player_turn(self):
        self.player.reset_block()
        self.dice_pool.roll(3)
        self.selected_dice_idx = None
        self.status_message = "Выберите кубик, затем карту."

    def select_dice(self, index: int):
        """Выбор кубика кликом мыши."""
        if 0 <= index < len(self.dice_pool):
            self.selected_dice_idx = index
            val = self.dice_pool[index]
            self.status_message = f"Выбран кубик [{val}]. Теперь кликните по карте."

    def try_play_card(self, card_index: int):
        """Попытка сыграть карту выбранным кубиком."""
        if self.game_state != "PLAYING":
            return

        if self.selected_dice_idx is None:
            self.status_message = "Сначала кликните по кубику!"
            return

        card = self.player.deck[card_index]
        dice_val = self.dice_pool[self.selected_dice_idx]

        if card.can_use(dice_val):
            self.dice_pool.pop(self.selected_dice_idx)
            self.selected_dice_idx = None
            card.play(self.player, self.enemy, dice_val)
            self.status_message = f"Использована '{card.name}' ({dice_val})!"
            self._check_enemy_status()
        else:
            self.status_message = f"Кубик [{dice_val}] не подходит! Нужно: {card.condition_desc}"

    def end_player_turn(self):
        """Завершение хода игрока и атака врага."""
        if self.game_state != "PLAYING":
            return

        self.enemy.reset_block()
        self.enemy.take_turn(self.player)

        if not self.player.is_alive():
            self.game_state = "GAME_OVER"
            self.status_message = "ВЫ ПОГИБЛИ! Нажмите R для рестарта."
        else:
            self.start_player_turn()

    def _check_enemy_status(self):
        """Проверка, повержен ли текущий враг."""
        if not self.enemy.is_alive():
            self.current_enemy_idx += 1
            if self.current_enemy_idx < len(self.enemies):
                self.enemy = self.enemies[self.current_enemy_idx]
                self.start_player_turn()
                self.status_message = f"Враг повержен! Появился {self.enemy.name}!"
            else:
                self.game_state = "VICTORY"
                self.status_message = "ПОБЕДА! Все враги уничтожены!"
