import pytest

from enigma.bombe import Bombe
from tests.menu_test_data import BOMBE_TEST2 as B2
from tests.menu_test_data import BOMBE_TEST_EASY1 as BE


def test_bombe_init() -> None:
    bombe = Bombe(menu=B2.menu, left_rotor=B2.left_rotor, middle_rotor=B2.middle_rotor,
                  right_rotor=B2.right_rotor, reflector=B2.reflector)
    test_char = B2.menu['config']['in']
    assert bombe.test_char == test_char
    assert bombe.identity_scrambler.window_letters == "ZZB"  # B2 doesn't use 1st or 2nd menu positions
    bombe.light_character()
    assert bombe.register_lit_chars == test_char
    assert bombe.current_sum == 1


@pytest.mark.parametrize("bombe_test_data", (BE, B2))
def test_bombe_step_and_test(bombe_test_data: Bombe) -> None:
    bombe = Bombe(
        menu=bombe_test_data.menu,
        left_rotor=bombe_test_data.left_rotor,
        middle_rotor=bombe_test_data.middle_rotor,
        right_rotor=bombe_test_data.right_rotor,
        reflector=bombe_test_data.reflector)

    # set identity scrambler to the known enigma starting position
    while bombe.identity_scrambler.window_letters != bombe_test_data.current_window_3:
        bombe.spin_scramblers()

    # we should get a drop straight away, and not get another in the next random position
    for i in range(2):
        bombe.step_and_test()
        print("i=", i, ", drops=", bombe.drops)
        assert set(bombe.drops.keys()) == {bombe_test_data.current_window_3}
        assert bombe.drops[bombe_test_data.current_window_3] != 26
