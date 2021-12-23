import scope_creep
from unittest import mock


def test_board_class():
    b = scope_creep.Board()
    assert b


def test_get_adjacent_idxs():
    b = scope_creep.Board()
    result = b.get_adjacent_idxs(15)
    assert result == [4, 5, 6, 14, 16, 24, 25, 26]

    result = b.get_adjacent_idxs(0)
    assert result == [1, 10, 11]

    result = b.get_adjacent_idxs(77)
    assert result == [66, 67, 76]


def test_game_over():
    b = scope_creep.Board()
    b.gameover = True
    assert b.run() is None
    # this will run an endless loop if there's a problem


def test_apply_enemy_movement():
    # basic movement
    b = scope_creep.Board()
    b.apply_enemy_movement(72, 73)
    assert b.grid[72] == '_'
    assert b.grid[73] == '1'

    # lvl 1 enemy died from stepping on + cell
    b.grid[74] = '+'
    b.apply_enemy_movement(73, 74)
    assert b.enemies_killed == 1
    assert b.grid[73] == '_'
    assert b.grid[74] == '_'

    # enemy killed you
    b.apply_enemy_movement(73, 7)
    assert b.gameover is True

    # enemies merged and leveled up
    b.apply_enemy_movement(50, 60)
    assert b.grid[60] == '2'
    assert b.grid[50] == '_'

    # enemy took a damage from stepping on + cell
    b.grid[51] = '+'
    b.apply_enemy_movement(60, 51)
    assert b.grid[51] == '1'
    assert b.grid[60] == '_'


def test_decide_enemy_movement():
    # start with all options '_'
    b = scope_creep.Board()
    option_idxs = [0, 1, 2, 3, 4, 5]
    assert b._decide_enemy_movement(option_idxs) in option_idxs

    # when player is in range, move there
    b.grid[0] = 'A'
    assert b._decide_enemy_movement(option_idxs) == 0

    # make all options '+'
    for x in option_idxs:
        b.grid[x] = '+'
    assert b._decide_enemy_movement(option_idxs) in option_idxs

    # if another enemy is the only option other than +, then take it
    b.grid[5] = '1'
    assert b._decide_enemy_movement(option_idxs) == 5

    # if an enemy and a '_' are in range, pick the '_'
    b.grid[2] = '_'
    b.grid[3] = '_'
    assert b._decide_enemy_movement(option_idxs) in [2, 3]


def test_perform_enemy_move():
    # enemy stack-leveling
    b = scope_creep.Board()
    b.grid[60] = '+'
    b.grid[61] = '+'
    b.grid[71] = '1'
    b.grid[70] = '1'
    b._perform_enemy_move(70)
    assert b.grid[71] == '2'
    assert b.grid[70] == '_'

    # enemy death
    b = scope_creep.Board()
    b.grid[60] = '+'
    b.grid[61] = '+'
    b.grid[71] = '+'
    b.grid[70] = '1'
    b._perform_enemy_move(70)
    assert b.enemies_killed > 0
    assert b.grid[70] == '_'
    assert '_' in [b.grid[60], b.grid[61], b.grid[71]]


def test_enemy_move_phase():
    b = scope_creep.Board()
    copy_grid = b.grid.copy()
    b.enemy_movement_phase()
    assert b.grid != copy_grid


def test_get_enemy_idxs():
    b = scope_creep.Board()
    enemy_idxs = b.get_enemy_idxs()
    for x in [50, 60, 61, 70, 71, 72]:
        assert x in enemy_idxs


def test_apply_your_move():
    b = scope_creep.Board()
    b.apply_your_move(7, 17)
    assert b.move_count == 1
    assert not b.gameover
    assert b.grid[7] == '+'
    assert b.grid[17] == 'A'


def test_prompt_you_for_move():
    b = scope_creep.Board()
    with mock.patch('builtins.input', return_value='D'):
        assert b.prompt_you_for_move(7) == 17

    # add test for re-prompting when input is invalid


def test_your_movement_phase():
    b = scope_creep.Board()
    with mock.patch('builtins.input', return_value='D'):
        b.your_movement_phase()
    assert b.gameover is False


def test_explosion_phase():
    b = scope_creep.Board()
    b.grid[50] = '1'
    b.grid[60] = '+'
    b.grid[61] = '+'
    b.grid[71] = '1'
    b.grid[70] = '1'
    b.explosion_phase()
    assert b.enemies_killed == 3
    for x in [50, 60, 61, 71, 70]:
        assert b.grid[x] == '_'

    b = scope_creep.Board()
    b.grid[50] = '2'
    b.grid[60] = '+'
    b.grid[61] = '+'
    b.grid[71] = '1'
    b.grid[70] = '1'
    b.explosion_phase()
    assert b.enemies_killed == 2
    assert b.grid[50] == '2'
    for x in [60, 61, 71, 70]:
        assert b.grid[x] == '_'
