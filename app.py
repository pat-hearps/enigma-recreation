import time

import streamlit as st

from enigma.bombe import Bombe
from enigma.design import BOMBE_CONVERGENCE
from tests.menu_test_data import BOMBE_TEST2

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
    bombe.spin_scramblers()
    position = bombe.identity_scrambler.window_letters
    st.session_state[POSITION] = position
    bombe.set_up_lineup_check()

st.write(f"Position = {position}")
graph = st.empty()
register_sum = st.empty()

fig = bombe.nx_setup()
graph.pyplot(fig)

while len(bombe.track_sums) - 1 < BOMBE_CONVERGENCE or len(set(bombe.track_sums[-BOMBE_CONVERGENCE:])) > 1:
    bombe.one_step_sync()
    fig = bombe.graph_nx()
    graph.pyplot(fig)
    register_sum.write(f"current sum = {bombe.current_sum} / step {bombe.check_iters}\n{bombe.track_sums}")
    if bombe.current_sum == 26:
        break
    time.sleep(WAIT_SLEEP_SEC)
