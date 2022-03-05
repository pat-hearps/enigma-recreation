import pytest

from enigma.menu import MenuMaker

crib = "TOTHEPRESIDENTOFTHEUNITEDSTATES"
encoded_crib = "CQNZPVLILPEUIKTEDCGLOVWVGTUFLNZ"


loop_data = [
    (0, 14, {frozenset(('E', 'I', 'P'))}),
    (3, 23, {frozenset(('E', 'I', 'P')), frozenset(('I', 'P', 'V')), frozenset(('N', 'O', 'T'))}),
    (14, 27, set())
]


@pytest.mark.parametrize("start, end, expected", loop_data)
def test_menumaker_loops(start: int, end: int, expected: set) -> None:
    menu_mkr = MenuMaker(crib=crib[start:end], encoded_crib=encoded_crib[start:end])
    menu_mkr.process_stuff()
    found_loops = set(frozenset(loop) for loop in menu_mkr.found_loops)
    assert found_loops == expected
    # assert 0

