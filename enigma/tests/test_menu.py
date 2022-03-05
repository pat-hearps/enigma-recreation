import pytest
from typing import Tuple

from enigma.menu import MenuMaker

CRIBS = {
    "welchman": {
        "crib_guess": "TOTHEPRESIDENTOFTHEUNITEDSTATES",
        "crib_cypher": "CQNZPVLILPEUIKTEDCGLOVWVGTUFLNZ"
    },
    "dermot_BB": {
        "crib_guess": "WETTERVORHERSAGE",
        "crib_cypher": "SNMKGGSTZZUGARLV"
    }
}


def get_crib_cypher(crib_set_name: str) -> Tuple[str, str]:
    crib_guess = CRIBS[crib_set_name]["crib_guess"]
    crib_cypher = CRIBS[crib_set_name]["crib_cypher"]
    return crib_guess, crib_cypher


gw_all_loops = {frozenset(('E', 'I', 'P')), frozenset(('I', 'P', 'V')), frozenset(('N', 'O', 'T'))}
loop_data = [
    ("welchman", 0, 14, {frozenset(('E', 'I', 'P'))}),
    ("welchman", 3, 23, gw_all_loops),
    ("welchman", 14, 27, set()),
    ("dermot_BB", 0, 30, {frozenset(('G', 'E', 'V', 'S', 'A', 'R'))})
]


@pytest.mark.parametrize("crib_set_name, start, end, expected", loop_data)
def test_menumaker_loops(crib_set_name: str, start: int, end: int, expected: set) -> None:
    crib_guess, crib_cypher = get_crib_cypher(crib_set_name)
    menu_mkr = MenuMaker(crib=crib_guess[start:end], encoded_crib=crib_cypher[start:end])
    menu_mkr.process_stuff()
    found_loops = set(frozenset(loop) for loop in menu_mkr.found_loops)
    assert found_loops == expected
    # assert 0

w_14_pairs = {'C': {0: 'T'}, 'D': {10: 'E'}, 'E': {4: 'P', 7: 'I', 10: 'D', 11: 'U'}, 'H': {3: 'Z'}, 'I': {7: 'E', 9: 'P', 12: 'N'}, 'K': {13: 'T'}, 'L': {6: 'R', 8: 'S'}, 'N': {2: 'T', 12: 'I'}, 'O': {1: 'Q'}, 'P': {4: 'E', 5: 'V', 9: 'I'}, 'Q': {1: 'O'}, 'R': {6: 'L'}, 'S': {8: 'L'}, 'T': {0: 'C', 2: 'N', 13: 'K'}, 'U': {11: 'E'}, 'V': {5: 'P'}, 'Z': {3: 'H'}}
dermot_pairs = {'A': {12: 'S', 13: 'R'}, 'E': {1: 'N', 4: 'G', 10: 'U', 15: 'V'}, 'G': {4: 'E', 5: 'R', 11: 'R', 14: 'L'}, 'H': {9: 'Z'}, 'K': {3: 'T'}, 'L': {14: 'G'}, 'M': {2: 'T'}, 'N': {1: 'E'}, 'O': {7: 'T'}, 'R': {5: 'G', 8: 'Z', 11: 'G', 13: 'A'}, 'S': {0: 'W', 6: 'V', 12: 'A'}, 'T': {2: 'M', 3: 'K', 7: 'O'}, 'U': {10: 'E'}, 'V': {6: 'S', 15: 'E'}, 'W': {0: 'S'}, 'Z': {8: 'R', 9: 'H'}}
pairs_data = [
    ("welchman", 0, 14, w_14_pairs),
    ("dermot_BB", 0, 30, dermot_pairs)
]


@pytest.mark.parametrize("crib_set_name, start, end, expected", pairs_data)
def test_menumaker_pairs(crib_set_name: str, start: int, end: int, expected: set) -> None:
    crib_guess, crib_cypher = get_crib_cypher(crib_set_name)
    menu_mkr = MenuMaker(crib=crib_guess[start:end], encoded_crib=crib_cypher[start:end])
    menu_mkr.do_pairs()
    assert menu_mkr.hipairs == expected
