from enigma.bombe import Bombe
from tests.menu_test_data import BOMBE_TEST1 as B1


def test_bombe_init() -> None:
    bombe = Bombe(menu=B1.menu, left_rotor=B1.left_rotor, middle_rotor=B1.middle_rotor,
                  right_rotor=B1.right_rotor, reflector=B1.reflector)
    assert bombe.test_char == 'A'
