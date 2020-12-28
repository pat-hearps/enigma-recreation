import pytest
from enigma.enigma import Enigma3
from enigma.design import entry, raw_rotors, forward_rotors, rev_rotors, notches, reflectors, i, ii, iii, iv, v, ROTORS, NOTCHES


@pytest.fixture
def eg() -> Enigma3:
    return Enigma3(left_rotor=iii, middle_rotor=ii, right_rotor=i, reflector='B', menu_link='AAA')


def test_basic_setup(eg) -> None:
    assert eg.left_rotor == iii
    assert eg.middle_rotor == ii
    assert eg.right_rotor == i
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


once_thru_dat_no_ring = [
    ("AAA", "GVURPWXIQJANZLYKMEOFBSTCHD", "KUXZRTAYHJPNQLSEIDVWCBFGOM"),
    # ("AAB", "DPGVRHFEYUOAQMWLNCZJKBITSX", "LVRAHGCFWTUPNQKBMEYXJDOZIS"), # depends if we define end as RRo or Entry
    ("AKA", "FLMGYCTIQWVBJPNUXRAKDESOZH", "SLFUVADZHMTBCOXNIRWGPKJQEY"),
    ("NAA", "LQTMKJSHVWCBOGDPRFZENXUAIY", "UMPBQGCWIJVZSXLKOTRNHYFEAD")
]

@pytest.mark.parametrize("menu_link, exp_forward, exp_reverse", once_thru_dat_no_ring)
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


full_data_no_ring = [
    ("AAA", "NFXUHBJERGOPWAKLSIQVDTMCZY"),
    ("AAB", "FWPOVAYMLRNIHKDCUJXZQEBSGT"),
    ("AKA", "WDXBSPYNVKJRQHTFMLEOZIACGU"),
    ("NAA", "UWZNJYRPKEISTDQHOGLMAXBVFC")
]


@pytest.mark.parametrize("menu_link, exp_out", full_data_no_ring)
def test_full_scramble_no_ring_settings(menu_link, exp_out, eg):
    eg.set_current_position(menu_link=menu_link)

    for in_char, expected in zip(entry, exp_out):
        ans = eg.full_scramble(in_char)
        assert ans == expected
