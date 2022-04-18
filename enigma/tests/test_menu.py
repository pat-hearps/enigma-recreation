from typing import Tuple

import pytest

from enigma.menu import MenuMaker

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


def get_crib_cypher(crib_set_name: str) -> Tuple[str, str]:
    crib_guess = CRIBS[crib_set_name]["crib__guess"]
    crib_cypher = CRIBS[crib_set_name]["crib_cypher"]
    return crib_guess, crib_cypher


gw_all_loops = {frozenset(['E', 'I', 'P']), frozenset(['I', 'P', 'V']), frozenset(['N', 'O', 'T']),
                frozenset(['D', 'E', 'I', 'N', 'T'])}
loop_data = [
    ("welchman", 0, 14, {frozenset(['E', 'I', 'P'])}),
    ("welchman", 2, 22, gw_all_loops),  # note this has been failing since added, indicates true problems in code
    ("welchman", 14, 27, set()),
    ("dermot_BB", 0, 30, {frozenset(['G', 'E', 'V', 'S', 'A', 'R'])}),
    ("basic", 0, 4, {frozenset(['A', 'B', 'C'])}),
    ("basic", 1, 7, {frozenset(['B', 'D', 'E', 'F'])})
]


@pytest.mark.parametrize("crib_set_name, start, end, expected", loop_data)
def test_menumaker_loops(crib_set_name: str, start: int, end: int, expected: set) -> None:
    crib_guess, crib_cypher = get_crib_cypher(crib_set_name)
    menu_mkr = MenuMaker(crib=crib_guess[start:end], encoded_crib=crib_cypher[start:end])
    menu_mkr.process_stuff()
    found_loops = set(frozenset(loop) for loop in menu_mkr.found_loops)
    assert found_loops == expected


# fmt: off
basic_link_idx = {'A': {0: 'B', 2: 'C'}, 'B': {0: 'A', 1: 'C', 3: 'D'}, 'C': {1: 'B', 2: 'A'}, 'D': {3: 'B', 4: 'E'}, 'E': {4: 'D'}}
w_14_link_idx = {'C': {0: 'T'}, 'D': {10: 'E'}, 'E': {4: 'P', 7: 'I', 10: 'D', 11: 'U'}, 'H': {3: 'Z'}, 'I': {7: 'E', 9: 'P', 12: 'N'}, 'K': {13: 'T'}, 'L': {6: 'R', 8: 'S'}, 'N': {2: 'T', 12: 'I'}, 'O': {1: 'Q'}, 'P': {4: 'E', 5: 'V', 9: 'I'}, 'Q': {1: 'O'}, 'R': {6: 'L'}, 'S': {8: 'L'}, 'T': {0: 'C', 2: 'N', 13: 'K'}, 'U': {11: 'E'}, 'V': {5: 'P'}, 'Z': {3: 'H'}}
dermot_link_idx = {'A': {12: 'S', 13: 'R'}, 'E': {1: 'N', 4: 'G', 10: 'U', 15: 'V'}, 'G': {4: 'E', 5: 'R', 11: 'R', 14: 'L'}, 'H': {9: 'Z'}, 'K': {3: 'T'}, 'L': {14: 'G'}, 'M': {2: 'T'}, 'N': {1: 'E'}, 'O': {7: 'T'}, 'R': {5: 'G', 8: 'Z', 11: 'G', 13: 'A'}, 'S': {0: 'W', 6: 'V', 12: 'A'}, 'T': {2: 'M', 3: 'K', 7: 'O'}, 'U': {10: 'E'}, 'V': {6: 'S', 15: 'E'}, 'W': {0: 'S'}, 'Z': {8: 'R', 9: 'H'}}
link_idx_data = [
    ("basic", 0, 5, basic_link_idx),
    ("welchman", 0, 14, w_14_link_idx),
    ("dermot_BB", 0, 30, dermot_link_idx)
]


@pytest.mark.parametrize("crib_set_name, start, end, expected", link_idx_data)
def test_menumaker_create_link_index(crib_set_name: str, start: int, end: int, expected: set) -> None:
    crib_guess, crib_cypher = get_crib_cypher(crib_set_name)
    menu_mkr = MenuMaker(crib=crib_guess[start:end], encoded_crib=crib_cypher[start:end])
    menu_mkr.count_characters()
    menu_mkr.create_link_index()
    assert menu_mkr.link_index == expected


best_chars_data = [
    ("basic", 0, 5, ('B',)),
    ("basic", 1, 7, ('B',)),
    ("welchman", 0, 14, ('E',)),
    ("dermot_BB", 0, 30, ('E', 'G', 'R'))
]
exp_loops = [
    [{frozenset(['B', 'A', 'C']): 'BACB'}],
    [{frozenset(['B', 'D', 'E', 'F']): 'BFEDB'}],
    [{frozenset(['E', 'P', 'I']): 'EIPE'}],
    [{frozenset(['A', 'E', 'S', 'V', 'R', 'G']): 'GRASVEG'}]
]
loops_data = [tuple(list(data) + exp) for data, exp in zip(best_chars_data, exp_loops)]


@pytest.mark.parametrize("crib_set_name, start, end, expected", best_chars_data)
def test_find_best_characters(crib_set_name: str, start: int, end: int, expected: set) -> None:
    crib_guess, crib_cypher = get_crib_cypher(crib_set_name)
    menu_mkr = MenuMaker(crib=crib_guess[start:end], encoded_crib=crib_cypher[start:end])
    menu_mkr.count_characters()
    menu_mkr.create_link_index()
    menu_mkr.find_best_characters()
    assert menu_mkr.best_characters == expected


@pytest.mark.parametrize("crib_set_name, start, end, best_chars, expected", loops_data)
def test_find_loops(crib_set_name: str, start: int, end: int, best_chars: tuple, expected: dict) -> None:
    crib_guess, crib_cypher = get_crib_cypher(crib_set_name)
    menu_mkr = MenuMaker(crib=crib_guess[start:end], encoded_crib=crib_cypher[start:end])
    menu_mkr.count_characters()
    menu_mkr.create_link_index()
    menu_mkr.find_best_characters()
    for best_char in best_chars:
        menu_mkr.find_loops(best_char)
    assert menu_mkr.found_loops.keys() == expected.keys()
