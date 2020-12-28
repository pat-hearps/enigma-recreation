import pytest
from enigma.enigma import Enigma3, Rotor, once_through_scramble
from enigma.design import entry, raw_rotors, forward_rotors, rev_rotors, notches, reflectors, i, ii, iii, iv, v, ROTORS, NOTCHES


@pytest.fixture
def eg() -> Enigma3:
    return Enigma3(left_rotor=iii, middle_rotor=ii, right_rotor=i, reflector='B', menu_link='AAA')


def test_rotor() -> None:
    rotor = Rotor(iv)
    assert rotor.rotor_type == iv
    assert rotor.cypher == 'ESOVPZJAYQUIRHXLNFTGKDCMWB'
    assert rotor.notch == 'J'
    assert rotor.index_cypher_forward == [4, 18, 14, 21, 15, 25, 9, 0, 24, 16, 20, 8, 17, 7, 23, 11, 13, 5, 19, 6, 10, 3, 2, 12, 22, 1]
    assert rotor.index_cypher_reverse == [7, 25, 22, 21, 0, 17, 19, 13, 11, 6, 20, 15, 23, 16, 2, 4, 9, 12, 1, 18, 10, 3, 24, 14, 8, 5]


def test_basic_enigma_setup(eg) -> None:
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
