import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from enigma.design import ENTRY, OTHER_SIDE, grey, invsoutmap, iomap, orange, red
from enigma.enigma import BaseEnigma, full_scramble
from enigma.utils import SPAM, get_logger

logger = get_logger(__name__)


def get_lit_chars(indict: dict) -> str:
    return ''.join([ch for ch, io in indict.items() if io == 1])


def get_lit_status(scrambler: BaseEnigma) -> str:
    return ' | '.join([get_lit_chars(s) for s in scrambler.status.values()])


class Bombe:

    def __init__(self, menu, left_rotor='I', middle_rotor='II', right_rotor='III', reflector='B'):
        """Needs to be initialised with a menu, which is a dictionary with a specific format of instructions
        for how scramblers are to be interconnected, and their starting positions"""
        self.left_rotor = left_rotor
        self.middle_rotor = middle_rotor
        self.right_rotor = right_rotor
        self.reflector = reflector
        self.scramblers = {}
        self.register = {'status': {char: 0 for char in ENTRY}}
        self.run_record = {}
        self.drops = {}

        self.menu = menu
        """Scrambler setup, creating a scrambler corresponding to each menu item"""
        for scr_id, descriptor_dict in self.menu.items():
            if scr_id == 'config':
                self.test_char = self.menu['config']['test_char']
                self.register['conxns'] = self.menu['config']['conxns']['in']
            else:
                self.scramblers[scr_id] = Scrambler(
                    self.left_rotor,
                    self.middle_rotor,
                    self.right_rotor,
                    self.reflector,
                    menu_link=descriptor_dict['menu_link'],
                    conx_in=descriptor_dict['conxns']['in'],
                    conx_out=descriptor_dict['conxns']['out'])
        self.lowest_scrambler_order = min([key for key in self.scramblers.keys()])
        self.identity_scrambler = self.scramblers[self.lowest_scrambler_order]

        # """Diagonal Board setup, could possible integrate into Scrambler setup loop above"""
        # self.diagonal_board_wiring = {}
        # for scr_id, descriptor_dict in self.menu.items():
        #     if scr_id == 'config':
        #         pass
        #     else:
        #         for inorout in ['in', 'out']:
        #             thisletter = descriptor_dict[inorout]
        #             if thisletter not in self.diagonal_board_wiring.keys():
        #                 self.diagonal_board_wiring[thisletter] = {scr_id: inorout}
        #             else:
        #                 self.diagonal_board_wiring[thisletter][scr_id] = inorout
        # # identity scrambler is just the first one in the sequence of letters used from the crib.
        # # will probably be 0/ZZZ unless that particular letter pair from the crib/cypher has not been
        # # used in the menu

    def pulse_connections(self):
        """Goes through every scrambler (once only), and updates in and out terminals with live feeds via conx_in and
        conx_out from its connected scramblers. Should be run iteratively to exhaustion."""
        for scr1id, scrambler in self.scramblers.items():
            # i.e for each scrambler in the enigma, we're going to loop through it's conxns['in'] and conxns['out']
            # dictionaries and check its connected scramblers to match any live wires
            for ior in ['in', 'out']:
                for scr2id, side in scrambler.conxns[ior].items():
                    # for this scrambler, go through the conxns 'in' or 'out' dict. It has the other scrambler you need to
                    # look at (scr2id, or the number/position label) and whether you're
                    # looking at the 'in' or 'out' side
                    for ch, io in self.scramblers[scr2id].status[side].items():
                        # look through the scrambler's status for that side (in or out)
                        if io == 1:   # and if it has a live wire
                            scrambler.status[ior][ch] = 1  # set the corresponding character in the conxns dict of the
            # logger.log(SPAM, f"pulse | scrambler {scr1id} status={scrambler.status}")
    # def sync_diagonal_board(self):
    #     """Current theory is ???"""
    #     for scr1id, scrambler in self.scramblers.items():
    #         for inorout in ['in', 'out']:
    #             # ie the single letter 'A', 'M' etc that is the menu connection
    #             connection_character = self.menu[scr1id][inorout]
    #             for character in self.diagonal_board_wiring.keys():
    #                 if scrambler.status[inorout][character] == 1:
    #                     for scr2id, side in self.diagonal_board_wiring[character].items():
    #                         self.scramblers[scr2id].status[side][connection_character] = 1

    def sync_test_register(self):
        """similar to pulse_connections in that it updates terminals of scramblers, but is solely about the
        interconnections between the test register and those scramblers which are connected to it"""
        for scr2id, side in self.register['conxns'].items():  # side = 'in' or 'out'
            other_scr_side = OTHER_SIDE[side]
            # for each of the scrambler terminals connected to the test register
            other_scrambler = self.scramblers[scr2id]
            for ch, io in other_scrambler.status[other_scr_side].items():
                # first sync any live wires from the scrambler to the test register
                if io == 1:
                    self.register['status'][ch] = 1
            for ch, io in self.register['status'].items():
                # but then also sync any live wires from the test register to the scrambler
                if io == 1:
                    other_scrambler.status[other_scr_side][ch] = 1

    def light_character(self):
        """just need a way to put in the initial character input into all of the scramblers"""
        self.register['status'][self.test_char] = 1

    def update_all(self):
        """For every scrambler, runs update() which passes live terminals through the scrambler - from in to out
        and vice versa, for whatever the current position is"""
        for _, scrambler in self.scramblers.items():
            scrambler.update()
            # lit_status = get_lit_status(scrambler)
            # logger.log(SPAM, f"scr {scr1id} after update | status={lit_status}")

    def spin_scramblers(self):
        """Runs step_enigma for all scramblers, spinning the right rotor once and perhaps the middle and left if
        they are in their notch positions"""
        for scrambler in self.scramblers.values():
            scrambler.step_enigma()

    def reset_scramblers_and_register(self):
        """ resets all scrambler statuses and test register to 0 for all alphabet characters"""
        for scrambler in self.scramblers.values():
            scrambler.reset_status()
        self.register['status'] = {char: 0 for char in ENTRY}

    @property
    def current_sum(self) -> int:
        return sum(self.register['status'].values())

    @property
    def register_lit_chars(self):
        return get_lit_chars(self.register['status'])

    def check_this_lineup(self):
        """For running to exhaustion on a particular bombe scrambler lineup.
        Loops through pulsing connections between scramblers and syncing back to the test register
        until the sum of live connections at the test register remains unchanged for two successive loops."""
        self.set_up_lineup_check()
        while len(set(self.track_sums[-5:])) != 1:
            # i.e. keep going until the register status is unchanged for 5 iterations
            # the 5 is somewhat arbitrary. Testing on one menu found no more than 3
            # continuous occurrences of an incomplete status but could be different
            # for other menus.
            self.one_step_sync()

    def set_up_lineup_check(self):
        """
        - Reset all scramblers and register (simulating the moment when no electrical current is passing through the machine
        as the scrambler electrical brushes move from one position to the next)
        - Send the first signal out from the register's test character.
        - Reset tracking variables"""
        self.reset_scramblers_and_register()   # first make sure all scrambler inputs/outputs (statuses) are reset to zero
        self.light_character()   # light up the one test character
        self.sync_test_register()              # do the first syncing of test register, sending the signal out to the
        # scramblers which are connected to the test register

        self.track_sums = [0, 1]
        self.lineup_iters = 0   # this is just to keep track of how many iterations it took to reach a steady status
        logger.log(
            SPAM,
            f"iter={self.lineup_iters}, current_sum={self.current_sum},  register={self.register_lit_chars}")

    def one_step_sync(self):
        """One step of the loop to exhaustion that sends an 'electrical pulse' (status=1) from each scrambler to other
        scramblers through the test register:
        - all scramblers with lit characters update the corresponding test register connection to also be lit
        - the test register then resyncs out all its lit characters to also be lit in each scrambler it is connected to
        """
        self.update_all()
        for scr1id, scrambler in self.scramblers.items():
            lit_status = get_lit_status(scrambler)
            logger.log(SPAM, f"update | scrambler {scr1id} status={lit_status}")
        self.pulse_connections()
#       self.sync_diagonal_board()
        self.sync_test_register()
        self.track_sums.append(self.current_sum)
        self.lineup_iters += 1
        logger.log(
            SPAM,
            f"iter={self.lineup_iters}, current_sum={self.current_sum}, register={self.register_lit_chars}")

    def step_and_test(self):
        """the main function to use for looping through all possible combinations of rotor positions,
        testing the connections at each step using check_this_lineup()"""
        self.spin_scramblers()
        self.check_this_lineup()
        self.run_record[self.identity_scrambler.window_letters] = (
            self.current_sum, self.lineup_iters, self.track_sums)
        if self.current_sum != 26:
            print('drop:  ', self.identity_scrambler.window_letters, 'livestatus:', self.current_sum)
            self.drops[self.identity_scrambler.window_letters] = self.current_sum

    def pdf_scrambler_statuses(self):
        """pdf = pandas dataframe
        Refreshes self.flash_scrambler_statuses variable to be a pandas dataframe summarising
        the current status (in==on/out==on) for each 26 alphabet letters for each of the scramblers in the Bombe"""
        bigdict = {}
        bigdict['REG'] = {k: ('X' if v == 1 else '') for k, v in self.register['status'].items()}
        for scr_id, scrambler in self.scramblers.items():
            littledict = {inorout: {char: (inorout[0].upper() if io == 1 else '') for char, io in letters.items()}
                          for inorout, letters in scrambler.status.items()}
            bigdict[scr_id] = {k1: v1 + littledict['out'][k1] for k1, v1 in littledict['in'].items()}
        self.flash_scrambler_statuses = pd.DataFrame(bigdict).T

    def nx_setup(self, scale=1, figsize=(15, 10), width_of_scrambler=0.1, height_of_scrambler=0.06):
        """For creating NetworkX graphs. Setting up base graph (BG), detailed graph (TG), figure and axes for displaying scrambler connections
        Will also effectively reset the nx Graphs"""
        self.BG = nx.Graph()
        scramblers_in_menu = [k if isinstance(k, int) else 'REG' for k in self.menu.keys()]
        self.BG.add_nodes_from(scramblers_in_menu)

        base_edges = set()
        for scr_id, descriptor_dict in self.menu.items():
            if scr_id == 'config':
                scr_id = 'REG'
            for inorout in ['in', 'out']:
                for connected_scrambler, ior in descriptor_dict['conxns'][inorout].items():
                    # the dictionary of connections that is the value for each 'conx_in/out' keys
                    base_edges.add(frozenset([scr_id, connected_scrambler]))  # set of sets so not to double up

        base_edges = [tuple(be) for be in base_edges]  # turn set of frozensets into list of tuples
        self.BG.add_edges_from(base_edges)
#         self.base_pos_for_nx = nx.circular_layout(self.BG,scale=scale)
        self.base_pos_for_nx = nx.spring_layout(self.BG, scale=scale)
        self.base_pos_for_nx['REG'] = np.array([0, -0.9])

        # This section for the detailed graph (TG)
        self.TG = nx.Graph()
        # this for-loop adds all nodes to the graph
        for scr_id in scramblers_in_menu:  # for each scrambler in the menu
            for ch in ENTRY:  # for each letter A-Z
                for i in ['I', 'O']:  # for each end (in/out) of the double-ended scrambler
                    if scr_id == 'REG':  # i = X (not I or O) if it's the register
                        i = 'X'
                    this_node_label = f"{scr_id}-{i}-{ch}"
                    self.TG.add_node(this_node_label)  # add a node to the graph
                    self.TG.nodes[this_node_label]["color"] = grey

        # this for-loop adds edges for scrambler connections to the graph
        self.inter_scr_edges = set()
        for scr_id, descriptor_dict in self.menu.items(
        ):                       # for each scrambler (scr_id) and its spec dict
            for inorout in ['in', 'out']:                          # go thru the conx_in and conx_out dicts
                if scr_id == 'config':   # this just for dealing with the register
                    first_node = 'REG-X-'
                else:
                    # label the start of the 1st node, with either I/O
                    first_node = f"{scr_id}-{iomap[inorout]}-"
                for connected_scrambler, ior in descriptor_dict['conxns'][inorout].items(
                ):          # go thru the in/out connections
                    second_node = f"{connected_scrambler}-{iomap[ior]}-"        # label the start of the 2nd node
                    for ch in ENTRY:                                                    # for each letter A-Z
                        # create 26 nodes with each of 1st/2nd node plus letter
                        self.inter_scr_edges.add(frozenset([first_node + ch, second_node + ch]))

        # bit of data reformatting for the edges
        self.inter_scr_edges = [list(fs) for fs in self.inter_scr_edges]
        for edge in self.inter_scr_edges:
            edge.append({'color': grey})
        self.inter_scr_edges = [tuple(fs) for fs in self.inter_scr_edges]
        self.TG.add_edges_from(self.inter_scr_edges)

        wrange_of_letters = list(np.linspace(-0.5 * width_of_scrambler, 0.5 * width_of_scrambler, 26))

        self.manual_pos = {}

        for node in self.TG.nodes():
            scr_id, io, ch = node.split('-')
            try:
                scr_id = int(scr_id)
            except ValueError:
                pass
            x, y = self.base_pos_for_nx[scr_id]

            if io == 'I':  # spacing apart the in from the out nodes
                y += -0.5 * height_of_scrambler  # 'in' (I) is below
            else:
                y += 0.5 * height_of_scrambler  # 'out' (O) is above

            x += wrange_of_letters[ENTRY.index(ch)]
            self.manual_pos[node] = np.array([x, y])

        self.colors = [self.TG[u][v]['color'] for u, v in self.TG.edges()]

        fig, ax = plt.subplots(figsize=figsize)
        nx.draw_networkx_nodes(self.BG, pos=self.base_pos_for_nx)
        nx.draw_networkx_labels(self.BG, pos=self.base_pos_for_nx)
        nx.draw_networkx_edges(self.TG, pos=self.manual_pos, edge_color=self.colors)

    def graph_nx(self, figsize=(15, 10), node_size=3):
        """First updates nx_graph edge colors based on current scrambler statuses,
        then redraws nx_graph visualisation"""
        for u, v in self.TG.edges():  # reset previously red to orange
            if self.TG[u][v]['color'] == red:
                self.TG[u][v]['color'] = orange
        for u, v in self.TG.nodes.items():
            if self.TG.nodes[u]['color'] == red:
                self.TG.nodes[u]['color'] = orange

        for scr_id, scrambler in self.scramblers.items():
            for ior in ['in', 'out']:
                for ch, onoff in scrambler.status[ior].items():
                    if onoff == 1:
                        first_live_node = f"{scr_id}-{iomap[ior]}-{ch}"
                        if self.TG.nodes[first_live_node]['color'] == grey:
                            self.TG.nodes[first_live_node]['color'] = red
                        cypher_node = f"{scr_id}-{invsoutmap[ior]}-{scrambler.full_scramble(ch)}"
                        # if statement below will add the intra_scrambler edges (letter in --> cypher out)
                        # stepwise as each node gets lit up
                        if (first_live_node, cypher_node) not in self.TG.edges():
                            self.TG.add_edge(first_live_node, cypher_node, color=red)

                        for bid, inout in scrambler.conxns[ior].items():
                            second_live_node = f"{bid}-{iomap[inout]}-{ch}"
                            try:
                                if self.TG.edges[(first_live_node, second_live_node)]['color'] == grey:
                                    self.TG.edges[(first_live_node, second_live_node)]['color'] = red
                            except IndexError:
                                if self.TG.edges[(second_live_node, first_live_node)]['color'] == grey:
                                    self.TG.edges[(second_live_node, first_live_node)]['color'] = red

        for ch, onoff in self.register['status'].items():
            if onoff == 1:
                first_live_node = f"REG-X-{ch}"
                for bid, inout in self.register['conxns'].items():
                    second_live_node = f"{bid}-{iomap[inout]}-{ch}"
                    try:
                        if self.TG.edges[(first_live_node, second_live_node)]['color'] == grey:
                            self.TG.edges[(first_live_node, second_live_node)]['color'] = red
                    except IndexError:
                        if self.TG.edges[(second_live_node, first_live_node)]['color'] == grey:
                            self.TG.edges[(second_live_node, first_live_node)]['color'] = red

        self.edge_colours = [self.TG[u][v]['color'] for u, v in self.TG.edges()]
        self.node_colours = [v['color'] for u, v in self.TG.nodes.items()]
        fig, ax = plt.subplots(figsize=figsize)
        nx.draw_networkx_nodes(self.BG, pos=self.base_pos_for_nx)
        nx.draw_networkx_labels(self.BG, pos=self.base_pos_for_nx)
        nx.draw_networkx_edges(self.TG, pos=self.manual_pos, edge_color=self.edge_colours)
        if node_size > 0:
            nx.draw_networkx_nodes(self.TG, pos=self.manual_pos, node_size=node_size, node_color=self.node_colours)


class Scrambler(BaseEnigma):
    """A Scrambler is a slightly adapted ENIGMA cypher, such that it has both an in and out end which are separate"""

    def __init__(
            self,
            left_rotor_type: str,
            middle_rotor_type: str,
            right_rotor_type: str,
            reflector_type: str,
            menu_link='ZZZ',
            conx_in={},
            conx_out={}):
        """rotors must be strings referring to either ['I','II','III','IV','V']
        reflector must be string, one of either ['B','C']"""
        super().__init__(
            left_rotor_type=left_rotor_type,
            middle_rotor_type=middle_rotor_type,
            right_rotor_type=right_rotor_type,
            reflector_type=reflector_type,
            current_window_3=menu_link,
            ring_settings_3="AAA")
        self.menu_link = menu_link
        self.status = {
            'in': {char: 0 for char in ENTRY},
            'out': {char: 0 for char in ENTRY}
        }
        self.conxns = {'in': conx_in, 'out': conx_out}

    def full_scramble(self, in_ch: str):
        return full_scramble(enigma=self, letter_in=in_ch)

    def update(self):
        """idea here is that the scrambler will check each of the 26 connections to see if they
        are live, and if so pass it through itself to light up the corresponding scramble (i.e. encyphered)
        character on the other side of  the scrambler"""
        for sides in [['in', 'out'], ['out', 'in']]:
            for char, io in self.status[sides[0]].items():
                if io == 0:
                    pass
                else:
                    self.status[sides[1]][self.full_scramble(char)] = 1

    def reset_status(self):
        """As it says on box, resets the status (dictionary of A-Z and 1/0 for each) all back to 0"""
        self.status['in'] = {char: 0 for char in ENTRY}
        self.status['out'] = {char: 0 for char in ENTRY}
