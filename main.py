import pygame
import sys
from entities import Player, Enemy
from cards import StrikeCard, ShieldCard, HeavyBlowCard
from engine import BattleEngine
from ui import GraphicalUI

def create_game() -> BattleEngine:
    player = Player(name="Искатель", max_hp=50)
    player.deck = [StrikeCard(), ShieldCard(), HeavyBlowCard()]
    
    enemies = [
        Enemy(name="Скелет-воин", max_hp=20, base_damage=5),
        Enemy(name="Темный рыцарь", max_hp=30, base_damage=7),
        Enemy(name="Некромант (Босс)", max_hp=45, base_damage=9),
    ]
    return BattleEngine(player, enemies)

def main():
    ui = GraphicalUI(width=900, height=600)
    engine = create_game()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                ui.handle_click(event.pos, engine)
                
            # Рестарт игры на клавишу R после победы или поражения
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                if engine.game_state in ("VICTORY", "GAME_OVER"):
                    engine = create_game()

        ui.draw(engine)
        clock.tick(60)

if __name__ == "__main__":
    main()
