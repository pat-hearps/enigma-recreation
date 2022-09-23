import os

os.environ["LOG_LEVEL"] = "INFO"

from enigma.design import ENTRY
from enigma.enigma import Enigma
from enigma.bombe import Bombe
from enigma.menu import MenuMaker
from tests.menu_test_data import BASIC_3CH as B3, BOMBE_TEST2 as B
from pprint import pformat, pprint



def main():

    crib = B.crib
    ring = 'AAA'
    # ring settings should always be 'AAA' for a bombe, as we ignore them
    enig = Enigma('I', 'II', 'III', 'B', ring_settings_3=ring, current_window_3='AAA')
    # bombe = Bombe(menu=B3)
    # mm = MenuMaker('ABCD')

    i = 0
    possible_settings = {}
    while i < 17577:
        enig.step_enigma()
        pre_cypher_position = enig.window_letters

        cypher = enig.cypher(crib)

        if i % 1000 == 0:
            print(f"{i}, pos={pre_cypher_position}, res={cypher}")

        mm = MenuMaker(crib, cypher)
        mm.run()
        if len(mm.found_loops.keys()) >= 2:
            check = set()
            all_keys = set(mm.found_loops.keys())
            for loop in mm.found_loops.keys():
                others = all_keys - {loop}
                for oth_loop in others:
                    check.add(len(oth_loop.intersection(loop)))
                if all((c <= 1 for c in check)):
                    print(f"found loops with {pre_cypher_position}! = \n", pformat(mm.found_loops.values()))
                    mm.network_graph(label=f"_{pre_cypher_position}_r{ring}")
                    possible_settings[pre_cypher_position] = mm.found_loops

        enig.set_window_letters(pre_cypher_position)
        i += 1


if __name__ == "__main__":
    main()
