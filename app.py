import time

import streamlit as st

from enigma.bombe import Bombe
from tests.menu_test_data import BOMBE_TEST2

CONVERGENCE = 4
WAIT_SLEEP_SEC = 0.1
POSITION = "position"

bombe_test_data = BOMBE_TEST2

bombe = Bombe(
    menu=bombe_test_data.menu,
    left_rotor=bombe_test_data.left_rotor,
    middle_rotor=bombe_test_data.middle_rotor,
    right_rotor=bombe_test_data.right_rotor,
    reflector=bombe_test_data.reflector)


if POSITION in st.session_state:
    position = st.session_state[POSITION]
else:
    position = bombe_test_data.current_window_3
    # or BGM works well

# set identity scrambler to the known enigma starting position
while bombe.identity_scrambler.window_letters != position:
    bombe.spin_scramblers(log=False)  # don't log all the setup steps


step = st.button("Step")
if step:
    bombe.step_and_test()
    position = bombe.identity_scrambler.window_letters
    st.session_state[POSITION] = position

st.write(f"Position = {position}")
graph = st.empty()
register_sum = st.empty()

fig = bombe.nx_setup()
graph.pyplot(fig)

progress = []
while len(progress) < CONVERGENCE or len(set(progress[-CONVERGENCE:])) > 1:
    bombe.cypher_signal_thru_all_scramblers()
    bombe.sync_scramblers_to_connected_scramblers()
    bombe.sync_test_register_with_connected_scramblers()
    progress.append(bombe.current_sum)
    fig = bombe.graph_nx()
    graph.pyplot(fig)
    register_sum.write(f"current sum = {bombe.current_sum} / step {len(progress)}")
    time.sleep(WAIT_SLEEP_SEC)
