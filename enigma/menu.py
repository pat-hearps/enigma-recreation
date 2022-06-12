from collections import Counter, defaultdict
from copy import deepcopy
from pprint import pformat
from typing import Dict, List

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from enigma.constants import MENU as M
from enigma.design import ENTRY
from enigma.utils import SPAM, VERBOSE, get_logger, spaces

logger = get_logger(__name__)

LoopDict = Dict[float, str]


def convert_to_ZZ_code(position: int) -> str:
    """Convert a menu link position integer to a 3-letter ZZ code,
    with the 3rd letter equal to the letter prior to the given position index
    in the alphabet"""
    middle_position = int(np.floor(position / 26))
    middle_char = ENTRY[middle_position - 1]
    char_before_this_position = ENTRY[position % 26 - 1]
    return f"Z{middle_char}{char_before_this_position}"


class MenuMaker:

    def __init__(self, crib, encoded_crib):
        logger.info(f"prepping menu, crib   = {crib}")
        logger.info(f"prepping menu, cypher = {encoded_crib}")
        self.crib: str = crib
        self.encoded_crib: str = encoded_crib
        self.pairs: Dict[int, set] = {}
        self.char_counts: Dict[str, int] = {}
        self.best_characters: List[str] = []
        self.link_index: Dict[str, dict] = {}
        self.found_loops: Dict[frozenset, str] = {}
        self.dead_ends: Dict = {}
        self.pfx: str = ""
        self.menu: dict = {}
        # positions_in_out = dict mapping for each position, which letter is in (crib), which is out (cypher), ZZ code
        self.base_menu_positions = {}
        # pairs_to_positions = dict mapping frozenset of pair of letters, to which position(s) they occur at
        self.pairs_to_positions = defaultdict(list)
        for pos, (in_ch, out_ch) in enumerate(zip(crib, encoded_crib)):
            self.base_menu_positions[pos] = {M.IN: in_ch, M.OUT: out_ch, M.LINK: convert_to_ZZ_code(pos)}
            pair_key_set = frozenset([in_ch, out_ch])
            self.pairs_to_positions[pair_key_set].append(pos)

    def run(self):
        """MAIN ENTRYPOINT FUNCTION - find all loops & deadends, then add connections to menu"""
        self.search_menu_structure()
        logger.debug(f"identified {len(self.found_loops)} loops:\n{self.found_loops}")
        logger.debug(f"identified {len(self.dead_ends)} dead ends:\n{self.dead_ends}")
        if self.found_loops:
            self.prep_menu()
        else:
            logger.info("No loops found, no menu can be made")

    def search_menu_structure(self):
        """First orchestration method, for finding all loops in a given crib"""
        self.count_characters()
        self.create_link_index()
        self.find_best_characters()
        self.found_loops, self.dead_ends = {}, {}  # reset every time
        # TODO - if no loops found, could try starting from non-best characters?
        for char in self.best_characters:
            logger.debug(f"finding loops for char {char}")
            self.find_loops(char)

    def count_characters(self):
        """Create two attribute dictionaries:
        self.pairs:
            keys    = position along crib/cypher
            values  = set(two chars, 1 each from the crib & cypher at the position)
        self.char_counts:
            keys    = each unique character that appears in the crib/cypher
            values  = how many times the character occurs across both the crib/cypher (min 1)
        """
        # pairs = pairs of letters by their position in the crib <> encoded crib
        self.pairs = {i: {c, m} for i, (c, m) in enumerate(zip(self.crib, self.encoded_crib))}
        logger.log(VERBOSE, f"this crib-cypher has the char pairs: {self.pairs}")
        # char_counts = for each character, how many times does it occur
        # TODO just use Counter() here
        count = defaultdict(int)
        for char in sorted(''.join((self.crib, self.encoded_crib))):
            count[char] += 1
        self.char_counts = dict(count)
        logger.log(VERBOSE, f"with characters appearing with the frequencies: {self.char_counts}")

    def create_link_index(self):
        """Create a dictionary referencing the links between characters and where they occur
        self.link_index:
            keys    = each unique character that appears in the crib/cypher
            values  = dictionary indexing which other characters link to it and where:
                        keys    = the position of the link (int along the crib/cypher)
                        values  = which other character is part of the link
        """
        for character in self.char_counts.keys():
            link_idx = {pos: (pair - {character}).pop() for pos, pair in self.pairs.items() if character in pair}
            # logger.log(SPAM, f"index of links for char={character} is {link_idx}")
            self.link_index[character] = link_idx
        # link_index = for each char in links, what other chars are they linked to at what position
        # result is dict of k=position, v=char
        logger.debug(f"index of links are: {self.link_index}")

    def find_best_characters(self):
        """Find which characters occur the most in the crib/cypher,
        set these to self.best_characters
        """
        max_count = max(self.char_counts.values())
        self.best_characters = tuple(
            char for char, n_links in self.char_counts.items() if n_links == max_count
        )
        logger.debug(f"chars with the most links ({max_count}) are: {self.best_characters}")

    def find_loops(self, starting_character: str):
        """Starting from a particular character, iteratively explore all possible paths in a menu of linked characters,
        aiming to identify sequences where a 'loop' is formed where a circular path is possible."""
        # is really 'finding all possible loops' by brute-forcing traversing the network
        working_dict = {float(i + len(self.found_loops)): ''.join((starting_character, v))
                        for i, v in enumerate(self.link_index[starting_character].values())
                        }
        logger.log(VERBOSE, f"initial working dict is= {working_dict}")

        loop_count = 1
        while len(working_dict) > 0:
            self.pfx = f"loop itr={loop_count} |"
            working_dict = self.make_connections(working_dict, loop_count)
            loop_count += 1

    def make_connections(self, start_working_dict: LoopDict, loop_count: int):
        """Used to iterate through exploring all possible paths through linked characters in a menu
        For a given dict where values (chains) represent unique paths through the possible network of linked characters:
        - grows every chain of letters by 1, for each letter that can link to the end of the chain
        - parses the resulting chains to see whether any are dead ends, or successful loops. If neither, the chain is
          kept for another iteration
        """
        spc50 = spaces(50)

        grown_working_dict = self.grow_chains(start_working_dict, loop_count)
        logger.log(VERBOSE, f"{self.pfx} chains grown,\n{spc50}in={start_working_dict}\n{spc50}wd={grown_working_dict}"
                            f"\n{spc50}found_loops={self.found_loops}, deadends={self.dead_ends}")

        parsed_working_dict = self.parse_chains(grown_working_dict)
        logger.log(VERBOSE, f"{self.pfx} parsed,\n{spc50}in={grown_working_dict}\n{spc50}out={parsed_working_dict}"
                            f"\n{spc50}found_loops={self.found_loops}, deadends={self.dead_ends}")

        return parsed_working_dict

    def grow_chains(self, old_working_dict: LoopDict, loop_count: int):
        """For all the chains of letters in the working_dict, grow the chain by one letter, for each letter
        that the end is connected to. This may fork to create multiple chains from one original."""
        new_working_dict = deepcopy(old_working_dict)

        for iD, chain in old_working_dict.items():
            chain_end = chain[-1]
            chars_chain_end_links_to = self.link_index[chain_end]
            logger.log(SPAM, f"{self.pfx} chain={iD, chain} | end ({chain_end}) links to {chars_chain_end_links_to}")

            # check for deadends before trying to grow
            chain_only_links_to_one_char = len(chars_chain_end_links_to) == 1
            linked_char = list(chars_chain_end_links_to.values())[0]
            penultimate_char = chain[-2]
            if chain_only_links_to_one_char and linked_char == penultimate_char:
                logger.log(SPAM, f"{self.pfx} {chain} is a deadend")
                self.dead_ends[chain_end] = chain[::-1]  # reverse so deadend char is at start
                del new_working_dict[iD]

            else:
                # grow chain, creating new chain for each additional linked character
                for position_iD, conxn in enumerate(chars_chain_end_links_to.values()):
                    # adds fractional float value to new_key, smaller for each iteration, for tracking purposes
                    new_key = round(iD + position_iD / 10 ** loop_count, 5)
                    logger.log(SPAM, f"{self.pfx} saving key={new_key} = {chain}+{conxn}")
                    new_working_dict[new_key] = chain + conxn

        return new_working_dict

    def parse_chains(self, grown_working_dict: LoopDict):
        """This loop parses the results of the chain additions, whether it's found a deadend or loop, or neither
        if neither, chain is added back into the working dict for the next iteration
        """
        parsed_working_dict = {}
        for iD, chain in grown_working_dict.items():
            logger.log(SPAM, f"parsing chain {chain}")
            chain_count = Counter(chain)
            commonest_letter, occurrence_count = chain_count.most_common(1)[0]

            if chain[-1] in self.dead_ends.keys():
                pass
            elif occurrence_count == 1:  # just keep growing to see where it goes
                logger.log(SPAM, f"{self.pfx} keep going for {chain}")
                parsed_working_dict[iD] = chain

            elif occurrence_count == 2:
                # e.g. turns EINTON --> NTON, with knowledge that 2nd occurrence of commonest letter will be at the end
                only_loop_section = chain[chain.index(commonest_letter):]
                if len(only_loop_section) > 3:  # ie we're legit back to the start after a loop
                    self.add_to_found_loops(only_loop_section)
            else:
                raise ValueError(f"error parsing chain = {chain}, too many repeated characters: {chain_count}")

        return parsed_working_dict

    def add_to_found_loops(self, new_loop: str) -> None:
        """Makes sure candidate new loop is genuinely new. Selects only the portion of the chain representing the loop
         through a cycle of characters. This loop is converted to a frozenset for comparison against existing found
         loops, and for use as the key in dictionary of found_loops"""
        new_loop_set = frozenset(new_loop)
        logger.log(SPAM, f"checking potential new loop {new_loop}")
        already_found = False
        to_delete = []
        for found_loop in self.found_loops.keys():
            if found_loop.issubset(new_loop_set):
                already_found = True
            elif new_loop_set.issubset(found_loop):
                logger.log(VERBOSE, f"{self.pfx} previously found loop {found_loop} to be replaced by {new_loop_set}")
                to_delete.append(found_loop)

        for old_found_loop in to_delete:
            del self.found_loops[old_found_loop]

        if already_found:
            logger.log(SPAM, f"not adding {new_loop}")
        else:
            self.found_loops[new_loop_set] = new_loop
            logger.debug(f"{self.pfx} loop found = {new_loop}")

    def prep_menu(self):
        """Second main orchestration method, creates menu from found loops and deadends"""
        self.add_characters_to_menu()
        logger.log(VERBOSE, f"post adding characters to menu,\nlen={len(self.menu)} menu=\n{pformat(self.menu)}")
        self.configure_menu()
        logger.log(VERBOSE, f"post configure_menu,\nlen={len(self.menu)} menu=\n{pformat(self.menu)}")
        self.connections_add_to_menu()
        logger.log(VERBOSE, f"post connections_add_to_menu,\nlen={len(self.menu)} menu=\n{pformat(self.menu)}")

    def simplify_deadends(self):
        """Ignores deadends that are not connected loops in any way. Will preserve straight chains that
        link together separate loops. Doesn't change MenuMaker attributes, just returns list of simpler ends.
        Purpose is to reduce unneeded links and scramblers in menu."""
        simpler_deadends = []
        all_chars_in_loops = set().union(*self.found_loops.keys())
        for end, chain in self.dead_ends.items():
            end_connected_to_loop = set(chain) & all_chars_in_loops  # empty set if no letters in chain link to a loop
            if len(chain) <= 2 or not end_connected_to_loop:
                pass
            else:
                lopped_chain = chain.replace(end, '')
                simpler_deadends.append(lopped_chain)
        return simpler_deadends

    def add_characters_to_menu(self):
        """For each character in the menu network (obtained by combining loops and deadends),
        add each character's connections to other characters to the menu"""
        simpler_deadends = self.simplify_deadends()
        for chain in list(self.found_loops.values()) + simpler_deadends:
            logger.log(SPAM, f"adding characters from {chain}")
            for char, next_char in zip(chain[:-1], chain[1:]):
                self.add_item_to_menu(char, next_char)

    def add_item_to_menu(self, char: str, next_char: str):
        positions_of_this_pair = self.pairs_to_positions[frozenset([char, next_char])]
        for position in positions_of_this_pair:
            if position not in self.menu.keys():
                menu_data = self.base_menu_positions[position]
                self.menu[position] = menu_data
                logger.log(SPAM, f"added item to menu at {position} : {menu_data}")

    def configure_menu(self):
        """Adds extra item to menu as the bombe entrypoint, using a character
        that is linked to the most other characters"""
        letters_in_menu = ''.join([''.join((data['in'], data['out'])) for data in self.menu.values()])
        ranked_letters = Counter(letters_in_menu)
        test_char = ranked_letters.most_common(1)[0][0]
        self.menu[M.CONFIG] = {M.TEST_CHAR: test_char, M.LINK: 'QQQ', M.IN: test_char, M.OUT: test_char}

    def connections_add_to_menu(self):
        """For each character / position for each node in menu, define which other nodes connect to this one.
        Connections are defined directionally, i.e. an 'in' connection is different to an 'out' one.
        """
        for position, itemdict in self.menu.items():
            in_char = itemdict[M.IN]
            ins = self.define_connections(in_char, position)

            out_char = itemdict[M.OUT]
            outs = self.define_connections(out_char, position)
            logger.log(SPAM, f"position={position} out_char={out_char} ins={ins} outs={outs}")

            self.menu[position][M.CONXNS] = {M.IN: ins, M.OUT: outs}

    def define_connections(self, char: str, char_position: int) -> dict:
        """For a given character (at a char_position), compare against all other menu items excluding config
        Return dict of position: 'in'|'out' for each node in menu that connects to this char"""
        comparison_dict = {pos: node for pos, node in self.menu.items() if pos not in (char_position, M.CONFIG)}
        connections = {pos: io for pos, node in comparison_dict.items() for io in (M.IN, M.OUT) if node[io] == char}
        return connections

    def network_graph(self, reset_pos=True, label="", pos_delta=0.15):
        """Using networkx package to display connections of menu letters"""
        # generate nodes and edges directly from menu
        nodes, edges = set(), []
        for scr_id, data in self.menu.items():
            if scr_id == 'config':
                continue
            this_scr_in, this_scr_out = data['in'], data['out']
            nodes.update({this_scr_in, this_scr_out})
            edges.append((this_scr_in, this_scr_out, {'pos': scr_id, 'menu_link': data['menu_link']}))

        # create Graph (MultiDiGraph = directional with multiple parallel edges)
        self.MultiGraph = nx.MultiDiGraph()
        self.MultiGraph.add_nodes_from(nodes)
        self.MultiGraph.add_edges_from(edges)

        # create labels for each specific label component
        in_labels, out_labels, z_labels = dict(), dict(), dict()
        for u, v, d in self.MultiGraph.edges(data=True):
            in_labels[(u, v)] = 'in'
            out_labels[(u, v)] = 'out'
            z_labels[(u, v)] = f"{d['pos']} / {d['menu_link']}"

        # Draw menu network graph
        fig, ax = plt.subplots(figsize=(15, 15))

        if not reset_pos:
            pass
        else:
            self.pos = nx.spring_layout(self.MultiGraph, k=0.99, scale=1)

        nx.draw_networkx(self.MultiGraph, pos=self.pos)
        nx.draw_networkx_edge_labels(
            self.MultiGraph, pos=self.pos, edge_labels=in_labels, label_pos=1 - pos_delta, rotate=False, ax=ax
        )
        nx.draw_networkx_edge_labels(
            self.MultiGraph, pos=self.pos, edge_labels=out_labels, label_pos=pos_delta, rotate=False, ax=ax
        )
        nx.draw_networkx_edge_labels(
            self.MultiGraph, pos=self.pos, edge_labels=z_labels, label_pos=0.5, rotate=False, ax=ax
        )
        filepath = f"./figures/menu{label}.png"
        plt.savefig(filepath)
        logger.info(f"menu network diagram saved to {filepath}")
