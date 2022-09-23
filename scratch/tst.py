import os

os.environ["LOG_LEVEL"] = "VERBOSE"


from pprint import pformat, pprint
from tests.menu_test_data import BASIC_3CH as B3, BOMBE_TEST2 as B
from enigma.menu import MenuMaker
from enigma.bombe import Bombe
from enigma.enigma import Enigma
from enigma.design import ENTRY





def main():

    window_setting = B.current_window_3
    crib = B.crib
    cypher = B.cypher

    ig = Enigma(left_rotor_type=B.left_rotor, middle_rotor_type=B.middle_rotor, right_rotor_type=B.right_rotor,
                reflector_type=B.reflector, ring_settings_3=B.ring_settings_3, current_window_3=B.current_window_3)
    print(f"msg/crib = {crib}, cypher={cypher}")
    for i, ch in enumerate(crib):
        cyf = ig.cypher(ch)
        print(f"char={ch}, cypher received={cyf}, cypher expected={cypher[i]}")
    
    bombe = Bombe(menu=B.menu, left_rotor=B.left_rotor, middle_rotor=B.middle_rotor, 
                  right_rotor=B.right_rotor, reflector=B.reflector)
    
    while bombe.identity_scrambler.window_letters != window_setting:
        bombe.spin_scramblers(log=False)
        
    print(B.menu)
    for _ in range(2):
        print("===========NEXT============\nwindow=", bombe.identity_scrambler.window_letters)
        bombe.step_and_test()
    
        print(f"drops={bombe.drops}")
    
    # # print(bombe.register['conxns'])
    



if __name__ == "__main__":
    main()
