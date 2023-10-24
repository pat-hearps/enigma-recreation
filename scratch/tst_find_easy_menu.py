import os
from pprint import pprint

os.environ["LOG_LEVEL"] = "VERBOSE"

from enigma.design import ENTRY
from enigma.enigma import Enigma
from enigma.bombe import Bombe
from enigma.menu import MenuMaker
from tests.menu_test_data import BASIC_3CH as B3, BOMBE_TEST2 as B2

def main():
    # ring settings should always be 'AAA' for a bombe, as we ignore them
    enig = Enigma('I', 'II', 'III', 'B', ring_settings_3='AAA', current_window_3='AAA')
    # bombe = Bombe(menu=B3)
    # mm = MenuMaker('ABCD')
    
    base_crib = 'CBA'
    desired_res = set(base_crib[:3])
    
    for char in ENTRY:
        crib = base_crib + char
    
        found = False
        i = 0
        while i < 17577:
            enig.step_enigma()
            pre_cypher_position = enig.window_letters
            
            res = enig.cypher(crib)
            
            if i % 1000 == 0:
                print(f"{i}, pos={pre_cypher_position}, res={res}")

            if set(res) == desired_res:
                found = True
                
                answer = pre_cypher_position
                print("got answer=", pre_cypher_position)
                break
            
            enig.set_window_letters(pre_cypher_position)
            i += 1

        enig.set_window_letters(answer)
        for c in crib:
            print(c, enig.cypher(c))
            
        mm = MenuMaker(crib, res)
        mm.run()
        if mm.found_loops:
            print("found loop! = ", mm.found_loops)
            break
        
    pprint(mm.menu)



if __name__ == "__main__":
    main()