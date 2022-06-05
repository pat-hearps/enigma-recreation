from enigma.bombe import Bombe
from tests.menu_test_data import BOMBE_TEST2 as B2
from tests.menu_test_data import BOMBE_TEST_EASY1 as BE


def test_bombe_init() -> None:
    bombe = Bombe(menu=B2.menu, left_rotor=B2.left_rotor, middle_rotor=B2.middle_rotor,
                  right_rotor=B2.right_rotor, reflector=B2.reflector)
    test_char = B2.menu['config']['in']
    assert bombe.test_char == test_char
    assert bombe.identity_scrambler.window_letters == "ZZZ"
    bombe.light_character()
    assert bombe.register_lit_chars == test_char
    assert bombe.current_sum == 1


def test_bombe_easy() -> None:
    bombe = Bombe(menu=BE.menu, left_rotor=BE.left_rotor, middle_rotor=BE.middle_rotor,
                  right_rotor=BE.right_rotor, reflector=BE.reflector)

    # set identity scrambler to the known enigma starting position
    while bombe.identity_scrambler.window_letters != BE.current_window_3:
        bombe.spin_scramblers()

    # we should get a drop straight away, and not get another in the next random position
    for _ in range(2):
        bombe.step_and_test()
        assert bombe.drops == {BE.current_window_3: 1}
