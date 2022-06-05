from enigma.bombe import Bombe
from tests.menu_test_data import BOMBE_TEST2 as B2


def test_bombe_init() -> None:
    bombe = Bombe(menu=B2.menu, left_rotor=B2.left_rotor, middle_rotor=B2.middle_rotor,
                  right_rotor=B2.right_rotor, reflector=B2.reflector)
    test_char = B2.menu['config']['in']
    assert bombe.test_char == test_char
    assert bombe.identity_scrambler.window_letters == "ZZZ"
    bombe.light_character()
    assert bombe.register_lit_chars == test_char
