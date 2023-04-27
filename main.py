"""
               ______  ______  __  ______  __  __    
              /\  ___\/\  __ \/\ \/\  ___\/\ \_\ \   
              \ \___  \ \  _-/\ \ \ \ \___\ \____ \  
               \/\_____\ \_\   \ \_\ \_____\/\_____\ 
                \/_____/\/_/    \/_/\/_____/\/_____/ 
         __  ______  __  __  ______  __   __  ______  __  __    
        /\ \/\  __ \/\ \/\ \/\  __ \/\ "-.\ \/\  ___\/\ \_\ \   
       _\_\ \ \ \/\ \ \ \_\ \ \  __<\ \ \-.  \ \  __\  \____ \  
      /\_____\ \_____\ \_____\ \_\ \_\ \_\ "\_\ \_____\/\_____\ 
      \/_____/\/_____/\/_____/\/_/ /_/\/_/ \/_/\/_____/\/_____/ 

"""

# GitHub : https://github.com/ImSumire/Spicy-Journey

__inspiration__ = (
    "Ghibli",  # Pour le style graphique
    "Minecraft",  # Pour la génération du monde
    "Animal Crossing",  # Pour la vue en top-down
    "Zelda Breath of the Wild",  # Pour le système de cuisine
)

### Importation des modules

import sys

# exit() quitte  simplement le script   Python, mais pas  l'environnement Python
# complet, tandis que sys.exit() quitte à  la fois  le script et l'environnement
# Python complet.
import json

# json est  meilleur que yaml car c'est  facile  de l'utiliser, il y a une
# meilleure compatibilité et de meilleures performances.
from time import perf_counter

import pygame
from pygame.locals import *

# Chargement des classes de source
from src.player import Player
from src.world import World
from src.gui import Gui


global seconds, tick, display, temp

### Création des constantes à partir du fichier config.json

# Charge les données du fichier config grâce à la librairie json
with open("config.json") as f:
    config: dict = json.load(f)

# Définition des constantes à partir du fichier config
WIDTH = config["dimensions"]["width"]
HEIGHT = config["dimensions"]["height"]
FPS = config["fps"]
TITLE = config["title"]
X_CENTER, Y_CENTER = CENTER = (WIDTH // 2, HEIGHT // 2)


def handle_events():
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            # Activer l'écran de débogage, échange la valeur booléenne
            if event.key == K_F3:
                gui.debug = not gui.debug

            elif event.key == K_a:
                # Position actuelle du joueur
                x, y = player.pos

                # Position fixée du joueur
                x_pos_fixed = world.center + round(x - int(x))
                y_pos_fixed = world.center + round(y - int(y))

                # Data aux coordonnées fixées
                pos = world.coords[y_pos_fixed][x_pos_fixed]

                # Si aux coordonnées fixées il y a un ingrédient
                if (
                    bool(round(pos[2]))  # S'il y a une végétation
                    and not pos[3] > world.water_level  # Si ce n'est pas de l'eau
                    and int(str(pos[2])[-2:])
                    in world.ingredients_range  # Si c'est un ingrédient
                    and world.vegetation_data[
                        int(x + x_pos_fixed),
                        int(y + y_pos_fixed),
                    ]  # S'il n'a pas été ramassé
                ):
                    # Récupérer l'ingrédient
                    gui.mixer.pok.play()
                    world.vegetation_data[
                        int(x + x_pos_fixed),
                        int(y + y_pos_fixed),
                    ] = False
                    ingredient = world.ingredients_list[
                        int(str(pos[2])[-2:]) - world.ingredients_range[0]
                    ]
                    if ingredient in player.inventory:
                        player.inventory[ingredient] += 1
                    else:
                        player.inventory[ingredient] = 1

        # Fermeture du jeu
        elif event.type == QUIT:
            pygame.quit()
            sys.exit()


def render():
    world.update(int(player.pos.x), int(player.pos.y))

    # Récupérer et afficher les sprites
    for sprite in world.get_sprites(player, tick):
        display.blit(sprite[0], (sprite[1], sprite[2]))

    # Dessiner l'interface graphique
    gui.draw()

    # Dessiner l'écran de débogage
    if gui.debug:
        gui.draw_debug(tick, seconds, clock.get_fps())

    # Dessiner le fondu
    if gui.fade.active:
        gui.fade.draw(screen)

    if gui.photo_fade.active:
        gui.photo_fade.draw(screen)

    pygame.display.flip()


if __name__ == "__main__":
    # Initialisation, définition du titre et des dimensions de la fenêtre
    pygame.init()
    pygame.display.set_caption(TITLE)  # "Spicy Journey"
    screen = pygame.display.set_mode((WIDTH, HEIGHT))  # (1280, 700)
    display = pygame.Surface(CENTER)  # (640, 350)
    clock = pygame.time.Clock()
    seconds: float = 0
    tick: int = 0

    # Création du monde
    world = World(WIDTH, HEIGHT)
    print("Seed : %s" % world.seed)
    print("Spawn : %s" % str(world.spawn))

    # Création du personnage
    player = Player(world)

    # Création du GUI (Graphical User Interface)
    gui = Gui(WIDTH, HEIGHT, screen, display, player, world)

    ### Démarrage du jeu

    while True:
        start = perf_counter()
        handle_events()  # Gestion des pressions sur les boutons
        player.update()  # Gère l'animation et les mouvements du joueur
        render()  # Effectue les calculs et dessine l'écran
        clock.tick(FPS)  # Limite les fps à la valeur inscrite dans les configs

        tick += 1  # Tick est la valeur représentative du temps en jeu
        seconds += perf_counter() - start  # Seconds est le temps passé en jeu
