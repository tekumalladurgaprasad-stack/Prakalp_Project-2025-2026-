import random

def read_game_state():

    state = {
        "player": {
            "name": "TestMon",
            "level": 10,
            "hp": random.randint(0,100),
            "max_hp": 100
        },

        "enemy": {
            "name": "EnemyMon",
            "level": 12,
            "hp": random.randint(0,100),
            "max_hp": 100
        },

        "moves": [
            {"name": "Move1","pp":10},
            {"name": "Move2","pp":10},
            {"name": "Move3","pp":10},
            {"name": "Move4","pp":10}
        ]
    }

    return state
