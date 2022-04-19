from typing import Tuple

import pytest

from enigma.menu import MenuMaker
from tests.menu_test_data import BASIC_3CH, BASIC_4CH, WELCHMAN_1L

CRIBS = {
    "basic": {
        "crib__guess": "ABCDDEF",
        "crib_cypher": "BCABEFB"
    },
    "welchman": {
        "crib__guess": "TOTHEPRESIDENTOFTHEUNITEDSTATES",
        "crib_cypher": "CQNZPVLILPEUIKTEDCGLOVWVGTUFLNZ"
    },
    "dermot_BB": {
        "crib__guess": "WETTERVORHERSAGE",
        "crib_cypher": "SNMKGGSTZZUGARLV"
    }
}
# sub_cribs define subsections of cribs by start:end indices
# which generate different loops and menus
SUB_CRIBS = {
    "welchman_1_loop": ("welchman", 0, 14),
    "welchman_4_loops": ("welchman", 2, 22),
    "welchman_no_loops": ("welchman", 14, 27),
    "dermot": ("dermot_BB", 0, 30),
    "basic_3ch_loop": ("basic", 0, 5),
    "basic_4ch_loop": ("basic", 1, 7)
}


def get_crib_cypher(crib_set_name: str) -> Tuple[str, str]:
    crib_key, start, end = SUB_CRIBS[crib_set_name]
    crib_guess = CRIBS[crib_key]["crib__guess"][start:end]
    crib_cypher = CRIBS[crib_key]["crib_cypher"][start:end]
    return crib_guess, crib_cypher


gw_all_loops = {frozenset(['E', 'I', 'P']), frozenset(['I', 'P', 'V']), frozenset(['N', 'O', 'T']),
                frozenset(['D', 'E', 'I', 'N', 'T'])}
loop_data = [
    ("welchman_1_loop", {frozenset(['E', 'I', 'P'])}),
    ("welchman_4_loops", gw_all_loops),  # note this has been failing since added, indicates true problems in code
    ("welchman_no_loops", set()),
    ("dermot", {frozenset(['G', 'E', 'V', 'S', 'A', 'R'])}),
    ("basic_3ch_loop", {frozenset(['A', 'B', 'C'])}),
    ("basic_4ch_loop", {frozenset(['B', 'D', 'E', 'F'])})
]


@pytest.mark.parametrize("crib_set_name, expected", loop_data)
def test_menumaker_loops(crib_set_name: str, expected: set) -> None:
    crib_guess, crib_cypher = get_crib_cypher(crib_set_name)
    menu_mkr = MenuMaker(crib=crib_guess, encoded_crib=crib_cypher)
    menu_mkr.search_menu_structure()
    found_loops = set(frozenset(loop) for loop in menu_mkr.found_loops)
    assert found_loops == expected


# I want deadends to be keys representing the individual character nodes that are truly
# the 'end' of a deadend chain. Values at the moment are just the shortest path from the most
# common letter to the deadend char, but this could change. Also not sure how to deal with
# shortest path when multiple 'most_common' letters e.g. dermot where both E & G have 4 connections
deadend_data = [
    ("basic_3ch_loop", {'E': 'BDE'}),
    ("basic_4ch_loop", {'A': 'BCA'}),
    ("welchman_1_loop", {'C': 'EINTC', 'D': 'ED', 'K': 'EINTK', 'U': 'EU', 'V': 'EPV'}),
    ("dermot", {'H': 'EGRZH', 'L': 'EGL', 'N': 'EN', 'U': 'EU', 'W': 'EVSW'})

]


@pytest.mark.parametrize("crib_set_name, expected", deadend_data)
def test_menumaker_deadends(crib_set_name: str, expected: dict) -> None:
    crib_guess, crib_cypher = get_crib_cypher(crib_set_name)
    menu_mkr = MenuMaker(crib=crib_guess, encoded_crib=crib_cypher)
    menu_mkr.search_menu_structure()
    assert menu_mkr.dead_ends.keys() == expected.keys()


# fmt: off
basic_link_idx = {'A': {0: 'B', 2: 'C'}, 'B': {0: 'A', 1: 'C', 3: 'D'}, 'C': {1: 'B', 2: 'A'}, 'D': {3: 'B', 4: 'E'}, 'E': {4: 'D'}}
w_14_link_idx = {'C': {0: 'T'}, 'D': {10: 'E'}, 'E': {4: 'P', 7: 'I', 10: 'D', 11: 'U'}, 'H': {3: 'Z'}, 'I': {7: 'E', 9: 'P', 12: 'N'}, 'K': {13: 'T'}, 'L': {6: 'R', 8: 'S'}, 'N': {2: 'T', 12: 'I'}, 'O': {1: 'Q'}, 'P': {4: 'E', 5: 'V', 9: 'I'}, 'Q': {1: 'O'}, 'R': {6: 'L'}, 'S': {8: 'L'}, 'T': {0: 'C', 2: 'N', 13: 'K'}, 'U': {11: 'E'}, 'V': {5: 'P'}, 'Z': {3: 'H'}}
dermot_link_idx = {'A': {12: 'S', 13: 'R'}, 'E': {1: 'N', 4: 'G', 10: 'U', 15: 'V'}, 'G': {4: 'E', 5: 'R', 11: 'R', 14: 'L'}, 'H': {9: 'Z'}, 'K': {3: 'T'}, 'L': {14: 'G'}, 'M': {2: 'T'}, 'N': {1: 'E'}, 'O': {7: 'T'}, 'R': {5: 'G', 8: 'Z', 11: 'G', 13: 'A'}, 'S': {0: 'W', 6: 'V', 12: 'A'}, 'T': {2: 'M', 3: 'K', 7: 'O'}, 'U': {10: 'E'}, 'V': {6: 'S', 15: 'E'}, 'W': {0: 'S'}, 'Z': {8: 'R', 9: 'H'}}
link_idx_data = [
    ("basic_3ch_loop", basic_link_idx),
    ("welchman_1_loop", w_14_link_idx),
    ("dermot", dermot_link_idx)
]


@pytest.mark.parametrize("crib_set_name, expected", link_idx_data)
def test_menumaker_create_link_index(crib_set_name: str, expected: set) -> None:
    crib_guess, crib_cypher = get_crib_cypher(crib_set_name)
    menu_mkr = MenuMaker(crib=crib_guess, encoded_crib=crib_cypher)
    menu_mkr.count_characters()
    menu_mkr.create_link_index()
    assert menu_mkr.link_index == expected


best_chars_data = [
    ("basic_3ch_loop", ('B',)),
    ("basic_4ch_loop", ('B',)),
    ("welchman_1_loop", ('E',)),
    ("dermot", ('E', 'G', 'R'))
]
exp_loops = [
    [{frozenset(['B', 'A', 'C']): 'BACB'}],
    [{frozenset(['B', 'D', 'E', 'F']): 'BFEDB'}],
    [{frozenset(['E', 'P', 'I']): 'EIPE'}],
    [{frozenset(['A', 'E', 'S', 'V', 'R', 'G']): 'GRASVEG'}]
]
loops_data = [tuple(list(data) + exp) for data, exp in zip(best_chars_data, exp_loops)]


@pytest.mark.parametrize("crib_set_name, expected", best_chars_data)
def test_find_best_characters(crib_set_name: str, expected: set) -> None:
    crib_guess, crib_cypher = get_crib_cypher(crib_set_name)
    menu_mkr = MenuMaker(crib=crib_guess, encoded_crib=crib_cypher)
    menu_mkr.count_characters()
    menu_mkr.create_link_index()
    menu_mkr.find_best_characters()
    assert menu_mkr.best_characters == expected


@pytest.mark.parametrize("crib_set_name, best_chars, expected", loops_data)
def test_find_loops(crib_set_name: str, best_chars: tuple, expected: dict) -> None:
    crib_guess, crib_cypher = get_crib_cypher(crib_set_name)
    menu_mkr = MenuMaker(crib=crib_guess, encoded_crib=crib_cypher)
    menu_mkr.count_characters()
    menu_mkr.create_link_index()
    menu_mkr.find_best_characters()
    for best_char in best_chars:
        menu_mkr.find_loops(best_char)
    assert menu_mkr.found_loops.keys() == expected.keys()


menu_data = [
    ("basic_3ch_loop", 6, BASIC_3CH),
    ("basic_4ch_loop", 7, BASIC_4CH),
    ("welchman_1_loop", 11, WELCHMAN_1L)
]


@pytest.mark.parametrize("crib_set_name, menu_length, expected", menu_data)
def test_menu_prep(crib_set_name: str, menu_length: int, expected: dict) -> None:
    crib_guess, crib_cypher = get_crib_cypher(crib_set_name)
    menu_mkr = MenuMaker(crib=crib_guess, encoded_crib=crib_cypher)
    menu_mkr.search_menu_structure()
    menu_mkr.prep_menu(length_of_menu=menu_length)
    assert menu_mkr.menu == expected
