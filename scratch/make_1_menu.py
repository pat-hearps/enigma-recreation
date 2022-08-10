import os

os.environ["LOG_LEVEL"] = "VERBOSE"

from tests.test_menu import get_crib_cypher
from enigma.design import ENTRY
from enigma.enigma import Enigma
from enigma.bombe import Bombe
from enigma.menu import MenuMaker
from tests.menu_test_data import BASIC_3CH as B3, BOMBE_TEST2 as B
from pprint import pformat, pprint



def main():
    # label = "welchman_4_loops"
    label = "welchman_1_loop"
    crib, cypher = get_crib_cypher(label)
    crib = B.crib
    window_setting = 'BFT'
    ring_setting = 'AAA'  # ring settings should always be 'AAA' for a bombe, as we ignore them
    enig = Enigma('I', 'II', 'III', 'B', ring_settings_3=ring_setting, current_window_3=window_setting)

    cypher = enig.cypher(crib)

    mm = MenuMaker(crib, cypher)
    mm.run()
    # pprint(mm.menu)
    # label = f"_better_{window_setting}_r{ring_setting}"
    mm.network_graph(label=label)
    print("loops=", mm.found_loops)
    print("dead_ends=", mm.dead_ends)
    # print("joining_chains=", mm.joining_chains)


if __name__ == "__main__":
    main()
