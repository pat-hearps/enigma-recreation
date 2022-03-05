import pytest

from enigma.menu import MenuMaker

crib = "TOTHEPRESIDENTOFTHEUNITEDSTATES"
encoded_crib = "CQNZPVLILPEUIKTEDCGLOVWVGTUFLNZ"


def test_menumaker() -> None:
    menu_mkr = MenuMaker(crib=crib, encoded_crib=encoded_crib)
    menu_mkr.process_stuff()
    assert 0

