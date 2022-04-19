from collections import Counter, defaultdict
from copy import deepcopy
from pprint import pformat
from typing import Dict, List

import matplotlib.pyplot as plt
import networkx as nx

from enigma.design import ENTRY
from enigma.utils import SPAM, VERBOSE, get_logger, spaces

logger = get_logger(__name__)

LoopDict = Dict[float, str]


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

    def search_menu_structure(self):
        """MAIN ENTRYPOINT METHOD for finding all loops in a given crib"""
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
                self.dead_ends[chain_end] = chain
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

        if not already_found:
            self.found_loops[new_loop_set] = new_loop
            logger.debug(f"{self.pfx} loop found = {new_loop}")

    def prep_menu(self, length_of_menu=12):
        """Second main entrypoint function, creates menu from found loops and deadends"""

        for loop in self.found_loops.values():
            try:
                self.loop_to_menu(mainloop=loop)
            except Exception as exc:
                logger.exception(f"error in loop_to_menu for {loop}")
                raise exc
        logger.log(VERBOSE, f"post loop_to_menu,\nmenu={pformat(self.menu)}")
        self.add_deadends_to_menu()
        logger.log(VERBOSE, f"post add_deadends_to_menu,\nmenu={pformat(self.menu)}")
        self.configure_menu()
        logger.log(VERBOSE, f"post configure_menu,\nmenu={pformat(self.menu)}")
        self.connections_add_to_menu()
        logger.log(VERBOSE, f"post connections_add_to_menu,\nmenu={pformat(self.menu)}")

    def loop_to_menu(self, mainloop):
        logger.log(SPAM, f"entry, mainloop={mainloop}")
        for char, next_char in zip(mainloop[:-1], mainloop[1:]):
            self.add_item_to_menu(char, next_char)

    def add_deadends_to_menu(self):
        for ends in sorted(list(self.dead_ends.values()), reverse=True):
            logger.log(SPAM, f"adding from deadend {ends}")
            for char, next_char in zip(ends[:-1], ends[1:]):
                self.add_item_to_menu(char, next_char)

    def add_item_to_menu(self, char: str, next_char: str):
        link_idx_rev = {_char: pos for pos, _char in self.link_index[char].items()}
        position_next_char = link_idx_rev[next_char]
        # note that I'm just picking the first one where there are double (or more) linkages
        # not sure if this matters for now or if its better to somehow include both linkages in the menu
        # revisit later depending on bombe methodology
        if position_next_char not in self.menu.keys():
            menu_val = {'in': char, 'out': next_char, 'menu_link': position_next_char}
            self.menu[position_next_char] = menu_val
            logger.log(SPAM, f"added item to menu at {position_next_char} : {menu_val}")

    def configure_menu(self):
        try:
            test_char = self.found_loops[0][0]
        except Exception:
            dend_string = "".join(m for m in self.dead_ends)
            count_of_dead_ends = {}
            for d in dend_string:
                if d not in count_of_dead_ends.keys():
                    count_of_dead_ends[d] = 1
                else:
                    count_of_dead_ends[d] += 1

            test_char = [
                k for k,
                v in count_of_dead_ends.items() if v == sorted(
                    count_of_dead_ends.values(),
                    reverse=True)[0]][0]

        self.menu['config'] = {}
        self.menu['config']['test_char'] = test_char
        self.menu['config']['menu_link'] = 'QQQ'
        self.menu['config']['in'] = test_char
        self.menu['config']['out'] = test_char
        self.menu['config']['conxns'] = {'in': {}, 'out': {}}

    def connections_add_to_menu(self):
        # this part adds in blank conx_in/out dicts and converts position to menulink 3-letter ZZ code
        for k, m in self.menu.items():
            if k == 'config':
                pass
            else:
                l = m['menu_link']  # noqa: E741
                l1 = ENTRY[l - 1]
                l2 = 'ZZ' + l1
                #     print(l)
                self.menu[k]['menu_link'] = l2
                self.menu[k]['conxns'] = {'in': {}, 'out': {}}
        #                 self.menu[k]['conx_out'] = {}

        # this part does the heavy lifting of populating the connections for each menu item
        for pos, mdict in self.menu.items():
            sin = mdict['in']
            for k, v in self.menu.items():
                if k == pos or k == 'config':
                    pass
                elif v['in'] == sin:
                    self.menu[pos]['conxns']['in'][k] = 'in'
                elif v['out'] == sin:
                    self.menu[pos]['conxns']['in'][k] = 'out'

            sout = mdict['out']
            for k, v in self.menu.items():
                if k == pos or k == 'config':
                    pass
                elif v['in'] == sout:
                    self.menu[pos]['conxns']['out'][k] = 'in'
                elif v['out'] == sout:
                    self.menu[pos]['conxns']['out'][k] = 'out'

    def network_graph(self, reset_pos=True):
        """Using networkx package to display connections of menu letters"""
        edges = {k: list(v) for k, v in self.pairs.items()}
        edges = [(v[0], v[1], {'label': str(k)}) for k, v in edges.items()]
        self.MultiGraph = nx.MultiGraph()
        self.MultiGraph.add_edges_from(edges)

        fig, ax = plt.subplots(figsize=(8, 8))

        if not reset_pos:
            pass
        else:
            self.pos = nx.spring_layout(self.MultiGraph, k=0.4, scale=1)

        nx.draw_networkx(self.MultiGraph, pos=self.pos)

        # labels = nx.get_edge_attributes(self.MultiGraph, 'label')
        # labels = {(k[0], k[1]): v for k, v in
        #           labels.items()}  # doesnt' seem to be able to deal with labels for multiples edges
        # edge_labels = nx.draw_networkx_edge_labels(self.MultiGraph, pos=self.pos, edge_labels=labels)
        plt.show(fig)
