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

