import streamlit as st

from enigma.bombe import Bombe
from tests.menu_test_data import BOMBE_TEST2

bombe_test_data = BOMBE_TEST2

bombe = Bombe(
    menu=bombe_test_data.menu,
    left_rotor=bombe_test_data.left_rotor,
    middle_rotor=bombe_test_data.middle_rotor,
    right_rotor=bombe_test_data.right_rotor,
    reflector=bombe_test_data.reflector)

# set identity scrambler to the known enigma starting position
while bombe.identity_scrambler.window_letters != bombe_test_data.current_window_3:
    bombe.spin_scramblers(log=False)  # don't log all the setup steps

bombe.step_and_test()
bombe.nx_setup()
st.write(bombe.TG)
