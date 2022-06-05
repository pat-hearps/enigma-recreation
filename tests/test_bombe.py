from enigma.bombe import Bombe
from tests.menu_test_data import BOMBE_TEST1 as B1


def test_bombe_init() -> None:
    bombe = Bombe(menu=B1.menu, left_rotor=B1.left_rotor, middle_rotor=B1.middle_rotor,
                  right_rotor=B1.right_rotor, reflector=B1.reflector)
    test_char = B1.menu['config']['in']
    assert bombe.test_char == test_char
    assert bombe.identity_scrambler.window_letters == "ZZZ"
    bombe.light_character()
    lit_characters = [char for char, status in bombe.register['status'].items() if status == 1]
    assert lit_characters == [test_char]
