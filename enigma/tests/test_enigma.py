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


def test_set_current_position(eg) -> None:
    menu_link = "HJP"
    eg.set_current_position(menu_link=menu_link)
    assert eg.current_position == menu_link
    assert eg.pos_left_rotor == entry.index(menu_link[0])
    assert eg.pos_mid_rotor == entry.index(menu_link[1])
    assert eg.pos_rgt_rotor == entry.index(menu_link[2])


dat_no_ring = [
    ("AAA", "GVURPWXIQJANZLYKMEOFBSTCHD", "KUXZRTAYHJPNQLSEIDVWCBFGOM"),
    # ("AAB", "DPGVRHFEYUOAQMWLNCZJKBITSX", "LVRAHGCFWTUPNQKBMEYXJDOZIS"), # depends if we define end as RRo or Entry
    ("AKA", "FLMGYCTIQWVBJPNUXRAKDESOZH", "SLFUVADZHMTBCOXNIRWGPKJQEY"),
    ("NAA", "LQTMKJSHVWCBOGDPRFZENXUAIY", "UMPBQGCWIJVZSXLKOTRNHYFEAD")
]

@pytest.mark.parametrize("menu_link, exp_forward, exp_reverse", dat_no_ring)
def test_once_thru_scramble_no_ring_settings(menu_link, exp_forward, exp_reverse, eg) -> None:
    eg.set_current_position(menu_link=menu_link)
    # forward direction
    for in_char, expected in zip(entry, exp_forward):
        ans = eg.once_thru_scramble(in_char, direction='forward', first_rotor=eg.right_rotor, pos1=eg.pos_rgt_rotor,
                                    second_rotor=eg.middle_rotor, pos2=eg.pos_mid_rotor,
                                    third_rotor=eg.left_rotor, pos3=eg.pos_left_rotor)
        assert ans == expected

    # reverse direction
    for in_char, expected in zip(entry, exp_reverse):
        ans = eg.once_thru_scramble(in_char, direction='back', first_rotor=eg.left_rotor, pos1=eg.pos_left_rotor,
                                    second_rotor=eg.middle_rotor, pos2=eg.pos_mid_rotor,
                                    third_rotor=eg.right_rotor, pos3=eg.pos_rgt_rotor)
        assert ans == expected
