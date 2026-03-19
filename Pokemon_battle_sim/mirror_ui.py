import numpy as np
import cv2

WIDTH = 800
HEIGHT = 500


def draw_text(screen, text, x, y):

    cv2.putText(
        screen,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255,255,255),
        2
    )


def draw_hp_bar(screen, x, y, hp, max_hp):

    ratio = hp / max_hp
    bar_width = 200

    cv2.rectangle(screen,(x,y),(x+bar_width,y+20),(0,0,255),-1)

    cv2.rectangle(
        screen,
        (x,y),
        (x+int(bar_width*ratio),y+20),
        (0,255,0),
        -1
    )


def render(state):

    screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

    enemy = state["enemy"]
    player = state["player"]

    draw_text(screen, f"{enemy['name']} Lv{enemy['level']}", 50, 60)
    draw_hp_bar(screen, 50, 80, enemy["hp"], enemy["max_hp"])

    draw_text(screen, f"{player['name']} Lv{player['level']}", 50, 220)
    draw_hp_bar(screen, 50, 240, player["hp"], player["max_hp"])

    draw_text(screen, "Moves:", 500, 200)

    for i, move in enumerate(state["moves"]):

        text = f"{i+1}. {move['name']}  PP:{move['pp']}"

        draw_text(screen, text, 500, 230 + i * 35)

    cv2.imshow("Battle Mirror", screen)

    cv2.waitKey(1)
