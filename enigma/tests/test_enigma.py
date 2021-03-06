import pytest
from enigma.enigma import Enigma3
from enigma.design import entry, raw_rotors, forward_rotors, rev_rotors, notches, reflectors


@pytest.fixture
def eg() -> Enigma3:
    return Enigma3(left_rotor='III', middle_rotor='II', right_rotor='I', reflector='B', menu_link='AAA')


def test_basic_setup(eg) -> None:
    assert eg.left_rotor == 'III'
    assert eg.middle_rotor == 'II'
    assert eg.right_rotor == 'I'
    assert eg.reflector == reflectors['B']
    assert eg.current_position == 'AAA'
    assert (eg.pos_left_rotor, eg.pos_mid_rotor, eg.pos_rgt_rotor) == (0, 0, 0)


def test_once_thru_scramble(eg) -> None:
    # forward direction
    for in_char, expected in zip(entry, "GVURPWXIQJANZLYKMEOFBSTCHD"):
        ans = eg.once_thru_scramble(in_char, direction='forward', first_rotor=eg.right_rotor, pos1=eg.pos_rgt_rotor,
                                    second_rotor=eg.middle_rotor, pos2=eg.pos_mid_rotor,
                                    third_rotor=eg.left_rotor, pos3=eg.pos_left_rotor)

        assert ans == expected

    # reverse direction
    for in_char, expected in zip(entry, "KUXZRTAYHJPNQLSEIDVWCBFGOM"):
        ans = eg.once_thru_scramble(in_char, direction='back', first_rotor=eg.left_rotor, pos1=eg.pos_left_rotor,
                                    second_rotor=eg.middle_rotor, pos2=eg.pos_mid_rotor,
                                    third_rotor=eg.right_rotor, pos3=eg.pos_rgt_rotor)

        assert ans == expected
