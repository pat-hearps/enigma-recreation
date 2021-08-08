import os

import pytest
from enigma.enigma import Enigma3, Rotor, once_thru_scramble, encode_thru_rotor, Enigma, Reflector, \
    encode_thru_reflector, full_scramble
from enigma.design import entry, raw_rotors, forward_rotors, rev_rotors, notches, REFLECTORS_CYPHER, i, ii, iii, iv, v, ROTORS, NOTCHES
from enigma.tests.factories import WindowFactory


def test_rotor_basic() -> None:
    rotor = Rotor(iv)
    assert rotor.rotor_type == iv
    assert rotor.cypher == 'ESOVPZJAYQUIRHXLNFTGKDCMWB'
    assert rotor.notch == 'J'
    assert rotor.index_cypher_forward == [4, 18, 14, 21, 15, 25, 9, 0, 24, 16, 20, 8, 17, 7, 23, 11, 13, 5, 19, 6, 10, 3, 2, 12, 22, 1]
    assert rotor.index_cypher_reverse == [7, 25, 22, 21, 0, 17, 19, 13, 11, 6, 20, 15, 23, 16, 2, 4, 9, 12, 1, 18, 10, 3, 24, 14, 8, 5]
    assert rotor.window_position == 0
    assert rotor.ring_position == 0
    assert rotor.actual_cypher_position == 0


rotor_offset_data = [
    ('A', 'A', 0, 0, 0),
    ('B', 'A', 1, 0, 1),
    ('A', 'B', 0, 1, 25),
    ('B', 'B', 1, 1, 0),
    ('C', 'F', 2, 5, 23),
    ('J', 'C', 9, 2, 7)
]


@pytest.mark.parametrize("wl_in, rs_in, exp_wp, exp_rp, exp_acp", rotor_offset_data)
def test_rotor_offset(wl_in, rs_in, exp_wp, exp_rp, exp_acp) -> None:
    rotor = Rotor(i, window_letter=wl_in, ring_setting=rs_in)
    assert rotor.window_position == exp_wp
    assert rotor.ring_position == exp_rp
    print(entry[rotor.actual_cypher_position], entry[exp_acp])
    assert rotor.actual_cypher_position == exp_acp

# all test data for rotor type I
rotor_encode_data = [
    ("A", "A", "EKMFLGDQVZNTOWYHXUSPAIBRCJ", True),
    ("C", "A", "KDJEBOTXLRMUWFVSQNYGZPAHCI", True),
    ("A", "D", "UFMHNPIOJGTYCQWRZBKAXVSDLE", True),
    ("Q", "W", "GOHXIPKQSLRMJWBFTZUCENDAYV", True),
    ("S", "M", "XKPTHNIQSBROMJUCVLWDYEGZFA", True),
    ("A", "A", "UWYGADFPVZBECKMTHXSLRINQOJ", False),
    ("C", "A", "WEYBDNTXZCAIKRFVQJPGLOMHSU", False),
    ("A", "D", "TRMXZBJDGISYCEHFNPWKAVOULQ", False),
    ("Q", "W", "XOTWUPACEMGJLVBFHKIQSZNDYR", False),
    ("S", "M", "ZJPTVYWEGNBRMFLCHKIDOQSAUX", False),
]
@pytest.mark.parametrize("window_letter, ring_setting, expected_data, forward", rotor_encode_data)
def test_rotor_encoding(window_letter, ring_setting, expected_data, forward):
    print(os.getenv("verbosity"))
    rotor = Rotor(rotor_type=i, window_letter=window_letter, ring_setting=ring_setting)
    for in_pos, exp_letter in enumerate(expected_data):
        ans_pos = encode_thru_rotor(rotor=rotor, entry_position=in_pos, forward=forward)
        ans_letter = entry[ans_pos]
        assert exp_letter == ans_letter


def test_rotor_step():
    rotor = Rotor(rotor_type=ii, window_letter="A", ring_setting="A")
    stepped = "BCDEFGHIJKLMNOPQRSTUVWXYZA"
    positions = list(range(1,26)) + [0]
    encoded = "JDKSIRUXBLHWTMCQGZNPYFVOEA"
    for exp, pos, cypher in zip(stepped, positions, encoded):
        rotor.step_rotor()
        assert rotor.window_letter == exp
        assert rotor.actual_cypher_position == pos
        assert encode_thru_rotor(rotor, entry_position=0) == (26 + entry.index(cypher) - pos) % 26


def test_reflector_setup() -> None:
    reflector = Reflector(reflector_type='B')
    assert reflector.reflector_type == 'B'
    assert reflector.cypher == {'A': 'Y', 'B': 'R', 'C': 'U', 'D': 'H', 'E': 'Q', 'F': 'S', 'G': 'L', 'H': 'D', 'I': 'P', 'J': 'X', 'K': 'N',
          'L': 'G', 'M': 'O', 'N': 'K', 'O': 'M', 'P': 'I', 'Q': 'E', 'R': 'B', 'S': 'F', 'T': 'Z', 'U': 'C', 'V': 'W',
          'W': 'V', 'X': 'J', 'Y': 'A', 'Z': 'T'}
    assert reflector.index_cypher_forward == {0: 24, 1: 17, 2: 20, 3: 7, 4: 16, 5: 18, 6: 11, 7: 3, 8: 15, 9: 23, 10: 13, 11: 6, 12: 14, 13: 10, 14: 12,
          15: 8, 16: 4, 17: 1, 18: 5, 19: 25, 20: 2, 21: 22, 22: 21, 23: 9, 24: 0, 25: 19}


dat_reflector = [
    ('B', 'YRUHQSLDPXNGOKMIEBFZCWVJAT'),
    ('C', 'FVPJIAOYEDRZXWGCTKUQSBNMHL')
]


@pytest.mark.parametrize("ref_type, exp", dat_reflector)
def test_encode_thru_reflector(ref_type: str, exp: str) -> None:
    reflector = Reflector(reflector_type=ref_type)
    for in_letter, exp_letter in zip(entry, exp):
        in_pos = entry.index(in_letter)
        res = encode_thru_reflector(reflector=reflector, entry_position=in_pos)
        assert exp_letter == entry[res]


# TODO delete, once old Enigma3 no longer used
@pytest.fixture
def eg3() -> Enigma3:
    return Enigma3(left_rotor=iii, middle_rotor=ii, right_rotor=i, reflector='B', current_window_3='AAA')


@pytest.fixture
def eg() -> Enigma:
    return Enigma(left_rotor_type=iii, middle_rotor_type=ii, right_rotor_type=i, reflector_type='B',
                  current_window_3="AAA", ring_settings_3="AAA")


# TODO delete, once old Enigma3 no longer used
def test_basic_enigma3_setup(eg3) -> None:
    assert eg3.left_rotor == iii
    assert eg3.middle_rotor == ii
    assert eg3.right_rotor == i
    assert eg3.reflector == REFLECTORS_CYPHER['B']
    assert eg3.current_position == 'AAA'
    assert (eg3.pos_left_rotor, eg3.pos_mid_rotor, eg3.pos_rgt_rotor) == (0, 0, 0)


def test_basic_enigma_setup(eg) -> None:
    assert eg.left_rotor.rotor_type == iii
    assert eg.middle_rotor.rotor_type == ii
    assert eg.right_rotor.rotor_type == i
    # assert eg.reflector == reflectors['B']
    assert eg.window_letters == 'AAA'
    assert type(eg.left_rotor) == Rotor
    assert type(eg.middle_rotor) == Rotor
    assert type(eg.right_rotor) == Rotor
    assert eg.left_rotor.actual_cypher_position == 0
    assert eg.middle_rotor.actual_cypher_position == 0
    assert eg.right_rotor.actual_cypher_position == 0
    assert type(eg.reflector) == Reflector
    assert eg.reflector.reflector_type == 'B'


def test_set_current_position(eg) -> None:
    window = WindowFactory()
    eg.set_window_letters(current_window_3=window.window())
    assert eg.window_letters == window.window()
    assert eg.left_rotor.window_letter == window.letter0
    assert eg.middle_rotor.window_letter == window.letter1
    assert eg.right_rotor.window_letter == window.letter2


# LR=III, MR=II, RR=I
once_thru_dat_no_ring = [
    ("AAA", "GVURPWXIQJANZLYKMEOFBSTCHD", "KUXZRTAYHJPNQLSEIDVWCBFGOM"),
    ("AAB", "DPGVRHFEYUOAQMWLNCZJKBITSX", "LVRAHGCFWTUPNQKBMEYXJDOZIS"), # depends if we define end as RRo or Entry
    ("AKA", "FLMGYCTIQWVBJPNUXRAKDESOZH", "SLFUVADZHMTBCOXNIRWGPKJQEY"),
    ("NAA", "YDGZXWFUIJPOBTQCESMRAKHNVL", "UMPBQGCWIJVZSXLKOTRNHYFEAD")
]


@pytest.mark.parametrize("current_window_3, exp_forward, exp_reverse", once_thru_dat_no_ring)
def test_once_through_scramble_no_ring_settings(current_window_3, exp_forward, exp_reverse, eg3) -> None:
    eg3.set_current_position(current_window_3=current_window_3)
    left_rotor = Rotor(rotor_type=eg3.left_rotor, window_letter=eg3.current_window_3[0])
    middle_rotor = Rotor(rotor_type=eg3.middle_rotor, window_letter=eg3.current_window_3[1])
    right_rotor = Rotor(rotor_type=eg3.right_rotor, window_letter=eg3.current_window_3[2])
    # forward direction
    for in_char, expected in zip(entry, exp_forward):
        ans_pos = once_thru_scramble(in_char, forward=True, left_rotor=left_rotor,
                                     middle_rotor=middle_rotor, right_rotor=right_rotor)
        assert ans_pos == expected

    # reverse direction
    for in_char, expected in zip(entry, exp_reverse):
        ans_pos = once_thru_scramble(in_char, forward=False, left_rotor=left_rotor,
                                     middle_rotor=middle_rotor, right_rotor=right_rotor)
        assert ans_pos == expected


full_data_no_ring = [
    ("AAA", "NFXUHBJERGOPWAKLSIQVDTMCZY"),
    ("AAB", "FWPOVAYMLRNIHKDCUJXZQEBSGT"),
    ("AKA", "WDXBSPYNVKJRQHTFMLEOZIACGU"),
    ("NAA", "UWZNJYRPKEISTDQHOGLMAXBVFC")
]


@pytest.mark.parametrize("current_window_3, exp_out", full_data_no_ring)
def test_full_scramble_no_ring_settings(current_window_3, exp_out, eg):
    eg.set_window_letters(current_window_3=current_window_3)

    for in_char, expected in zip(entry, exp_out):
        ans = full_scramble(eg, in_char)
        assert ans == expected


def test_step_enigma_1(eg):
    start_pos = 'AAP'
    eg.set_window_letters(current_window_3=start_pos)

    eg.step_enigma()
    assert eg.window_letters == 'AAQ'

    eg.step_enigma()
    assert eg.window_letters == 'ABR'


def test_step_enigma_2(eg):
    """Double step of middle rotor"""
    start_pos = 'KDO'
    eg.set_window_letters(current_window_3=start_pos)

    expected_windows = ['KDP', 'KDQ', 'KER', 'LFS', 'LFT', 'LFU']
    for exp in expected_windows:
        eg.step_enigma()
        assert eg.window_letters == exp

