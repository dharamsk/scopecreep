# Scope Creep
# A simple game...initially
from random import randrange, shuffle

MOVES_MAP = {
    "UL": -11, 
    "U": -10, 
    "UR": -9, 
    "L": -1, 
    "R": 1, 
    "DL": 9,
    "D": 10, 
    "DR": 11, 
}


class Board(object):
    # The board
    def __init__(self):
        # create the board
        self.grid = {x * 10 + y: '_' for x in range(8) for y in range(8)}

        # place player A
        self.grid[7] = 'A'

        # place enemies
        self.grid[50] = '1'
        self.grid[60] = '1'
        self.grid[61] = '1'
        self.grid[70] = '1'
        self.grid[71] = '1'
        self.grid[72] = '1'

        self.enemies_killed = 0
        self.move_count = 0
        self.gameover = False

        print("""

Welcome to Scope Creep!

This is a silly turn-based game where you try to stay alive and kill all enemies.
You don't have any weapons and the enemies will kill you on contact, but you leave 
behind a trail of Oxygen (+) when you move which hurts enemies when they come into 
contact with it. They'll avoid it if possible, so get crafty!

""")
        print(self)

        input("""

Map
    A: You
    1: Lvl 1 Enemy
    2: Lvl 2 Enemy
    3: etc..
    +: Oxygen
    _: Empty

    ~~~: Border (ignore it)
    Numbers around border: row/column identifiers. cell # = row + column


Win Condition: Kill all enemies and stay alive.


Rounds
    1. Enemies Move:
        Move one square (incl. diagonals).
        Will move randomly, but with this order of preference:
            A: Kill you. Game Over.
            _: Nothing.
            1: They merge with another enemy to create a higher level enemy (sum levels).
            +: Reduce level by 1 (die if level 1).
        The order in which enemies move is also random.

    2. You Move:
        Move one square (incl. diagonals).
        Moves are entered as L for Left, R for Right, UR for Up-Right, DL for Down-Left, etc

    3. Explosions:
        If an enemy is touching more + cells than its level, it dies, consuming all adjacent + cells (incl. diagonals).
            (Explosions all happen simultaneously, so a + cell can count toward multiple enemies exploding)
        Be careful though. If you aren't touching any + cells after the explosion phase, you die.


Other Things
    - When enemies die or Oxygen is consumed in an explosion, the cell becomes empty.

Hit ENTER to begin...

        """)

    def __str__(self):
        board_string = """
             0   1   2   3   4   5   6   7
        ~~~ ~~~ ~~~ ~~~ ~~~ ~~~ ~~~ ~~~ ~~~ ~~~
        ~~~|_-_|_-_|_-_|_-_|_-_|_-_|_-_|_-_|~~~
    10  ~~~|_-_|_-_|_-_|_-_|_-_|_-_|_-_|_-_|~~~
    20  ~~~|_-_|_-_|_-_|_-_|_-_|_-_|_-_|_-_|~~~
    30  ~~~|_-_|_-_|_-_|_-_|_-_|_-_|_-_|_-_|~~~
    40  ~~~|_-_|_-_|_-_|_-_|_-_|_-_|_-_|_-_|~~~
    50  ~~~|_-_|_-_|_-_|_-_|_-_|_-_|_-_|_-_|~~~
    60  ~~~|_-_|_-_|_-_|_-_|_-_|_-_|_-_|_-_|~~~
    70  ~~~|_-_|_-_|_-_|_-_|_-_|_-_|_-_|_-_|~~~
        ~~~ ~~~ ~~~ ~~~ ~~~ ~~~ ~~~ ~~~ ~~~ ~~~
        """
        for k, v in self.grid.items():
            board_string = board_string.replace('_-_', f'_{v}_', 1)
        return board_string

    def _game_over(self, reason_text):
        print("~~~ GAME OVER ~~~")
        print(reason_text)
        print(f"You killed {self.enemies_killed} enemies and made {self.move_count} moves!")
        print(self)
        self.gameover = True

    def _get_player_idx(self):
        x = [k for k, v in self.grid.items() if v == 'A']
        return x[0]

    def explosion_phase(self):

        exploding_idxs = list()
        for enemy in self.get_enemy_idxs():
            adjacent_idxs = self.get_adjacent_idxs(enemy)
            plus_idxs = [x for x in adjacent_idxs if self.grid[x] == '+']
            if len(plus_idxs) > int(self.grid[enemy]):
                print(f"Enemy in cell {enemy} triggered an explosion!")
                exploding_idxs += plus_idxs
                self.enemies_killed += 1
                self.grid[enemy] = '_'
        for idx in exploding_idxs:
            print(f"Cell {idx} was part of an explosion!")
            self.grid[idx] = '_'

        current_player_idx = self._get_player_idx()
        adjacent_idxs = self.get_adjacent_idxs(current_player_idx)
        if '+' not in [self.grid[x] for x in adjacent_idxs]:
            self._game_over("You were not touching any '+' cells at the end of the explosion phase")

    def your_movement_phase(self):

        # print board
        print(self)

        current_player_idx = self._get_player_idx()

        your_move_idx = self.prompt_you_for_move(current_player_idx)

        self.apply_your_move(current_player_idx, your_move_idx)

    def prompt_you_for_move(self, current_player_idx):

        valid_moves = self.get_adjacent_idxs(current_player_idx)
        valid_directions = [k for k, v in MOVES_MAP.items() if current_player_idx + v in valid_moves]
        
        your_move = input(f"You are in {current_player_idx}. Please enter a direction: ").upper()

        if your_move not in valid_directions:
            your_move = input(f"{your_move} is not valid. Please enter one of {valid_directions}: ").upper()

        your_move_idx = current_player_idx + MOVES_MAP[your_move]

        return your_move_idx

    def apply_your_move(self, current_player_idx, your_move_idx):
        effect = self.grid[your_move_idx]

        if effect.isnumeric():
            self._game_over(f"You stupidly ran into an enemy in cell {your_move_idx}")

        self.grid[your_move_idx] = 'A'
        self.grid[current_player_idx] = '+'
        self.move_count += 1

    def get_enemy_idxs(self):
        a = [k for k, x in self.grid.items() if x.isnumeric()]

        if not a:
            self._game_over("You WON! Congrats!")

        shuffle(a)
        return a

    def enemy_movement_phase(self):
        for enemy in self.get_enemy_idxs():
            # perform each enemy turn
            self._perform_enemy_move(enemy)

    def _perform_enemy_move(self, key):

        # get adjacent squares
        option_idxs = self.get_adjacent_idxs(key)
        
        # determine movement cell
        new_cell = self._decide_enemy_movement(option_idxs)

        # apply impact and update board
        self.apply_enemy_movement(key, new_cell)

    def _decide_enemy_movement(self, option_idxs):
        top_choices = list()
        current_selection = '+'

        # pick a cell
        for idx in option_idxs:
            value = self.grid[idx]

            # if cell is A, return it, this is the path we will take
            if value == 'A':
                return idx

            # elif cell is '_', this is the next preferred option
            elif value == '_':
                if current_selection == '_':
                    top_choices.append(idx)
                else:
                    current_selection = '_'
                    top_choices = [idx]

            # elif cell is a number, then prefer that option
            elif value.isnumeric() and current_selection != '_':
                if current_selection == '_':
                    continue
                elif current_selection == 'number':
                    top_choices.append(idx)
                else:
                    current_selection = 'number'
                    top_choices = [idx]

            # finally, move to a '+' cell if nothing else is available
            elif current_selection == '+':
                top_choices.append(idx)

        random_option = randrange(0, len(top_choices))
        # print(top_choices)
        return top_choices[random_option]

    def apply_enemy_movement(self, old_cell, new_cell):
        effect = self.grid[new_cell]
        origin = self.grid[old_cell]

        if effect == 'A':
            self._game_over(f"You were slain by an enemy in cell {old_cell}")
        elif effect.isnumeric():
            print(f"Enemy in cell {old_cell} has merged with {new_cell}!")
            self.grid[new_cell] = str(int(effect) + int(origin))
            self.grid[old_cell] = '_'
        elif effect == '+':
            if int(origin) < 2:
                print(f"Enemy in cell {old_cell} has been vanquished!")
                self.enemies_killed += 1
                self.grid[new_cell] = '_'
                self.grid[old_cell] = '_'
            else:
                print(f"Enemy in cell {old_cell} took one damage by entering {new_cell}!")
                self.grid[new_cell] = str(int(origin) - 1)
                self.grid[old_cell] = '_'
        elif effect == '_':
            print(f"{old_cell} moved to {new_cell}")
            self.grid[new_cell] = origin
            self.grid[old_cell] = '_'

    def run(self):
        turn_phases = [
            self.enemy_movement_phase,
            self.your_movement_phase,
            self.explosion_phase
        ]
        while not self.gameover:
            for callback in turn_phases:
                if self.gameover:
                    break
                callback()

    @staticmethod
    def get_adjacent_idxs(key):

        adjacent_squares = [key + x for k, x in MOVES_MAP.items()]

        return [x for x in adjacent_squares if 0 <= x <= 77 and x % 10 <= 7]


if __name__ == '__main__':
    b = Board()
    # print(b)
    b.run()

