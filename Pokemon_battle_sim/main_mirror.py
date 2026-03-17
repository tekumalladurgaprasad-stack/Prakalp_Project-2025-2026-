import time
from memory_reader import read_game_state
from mirror_ui import render


while True:

    state = read_game_state()

    if state:
        render(state)

    time.sleep(0.1)
