from collections import Counter, defaultdict
from copy import deepcopy
from typing import Dict, List

import matplotlib.pyplot as plt
import networkx as nx

from enigma.design import ENTRY
from enigma.utils import SPAM, VERBOSE, get_logger, spaces

logger = get_logger(__name__)


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

    def process_stuff(self):
        """MAIN ENTRYPOINT METHOD for finding all loops in a given crib"""
        self.count_characters()
        self.create_link_index()
        self.find_best_characters()
        self.found_loops, self.dead_ends = {}, {}  # reset every time
        # TODO - if no loops found, could try starting from non-best characters?
        for char in self.best_characters:
            logger.debug(f"finding loops for char {char}")
            self.find_loops(char)
        logger.debug(f'num dead ends b4 rationalising= {len(self.dead_ends)}')
        """TODO:
         - rationalise_to_list, unsub_list and get_smallest_loop appear to be dumb inefficient ways of picking
           out the unique loops from the many possible ways of defining them. Replace with something shorter and more
           intelligent based on using sets
         - why am I keeping the deadends, what are they for?"""
        self.dead_ends = self.rationalise_to_list(self.dead_ends)
        logger.debug(f'num dead ends after ration, b4 unsub= {len(self.dead_ends)}')
        self.dead_ends = self.unsub_list(self.dead_ends)
        logger.debug(f'num dead ends after unsub= {len(self.dead_ends)}')
        logger.debug(f'num loops b4 rationalising= {len(self.dead_ends)}')
        self.found_loops = self.rationalise_to_list(self.found_loops)
        logger.debug(f'num loops after ration, b4 unsub= {len(self.found_loops)}')
        self.found_loops = self.get_smallest_loop(self.found_loops)
        logger.debug(f'num loops after unsub= {len(self.found_loops)}')
        logger.debug(f'num dead ends b4 lose_redundant= {len(self.dead_ends)}')
        self.lose_redundant_deadends()
        logger.debug(f'num dead ends after lose_redundant= {len(self.dead_ends)}')

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
        # is really 'finding all possible loops' by brute-forcing traversing the chain
        working_dict = {i + len(self.found_loops) + 0.0: ''.join((starting_character, v))
                        for i, v in enumerate(self.link_index[starting_character].values())
                        }
        logger.log(VERBOSE, f"initial working dict is= {working_dict}")

        loop_count = 1
        while len(working_dict) > 0:
            self.pfx = f"loop itr={loop_count} |"
            working_dict = self.make_connections(working_dict, loop_count)
            loop_count += 1

    def make_connections(self, indict: Dict, loop_count: int):
        """Used to iterate through exploring all possible paths through linked characters in a menu
        For a given dict where values (chains) represent unique paths through the possible network of linked characters:
        - grows every chain of letters by 1, for each letter that can link to the end of the chain
        - parses the resulting chains to see whether any are dead ends, or successful loops. If neither, the chain is
          kept for another iteration
        """
        spc50 = spaces(50)

        grown_working_dict = self.grow_chains(indict, loop_count)
        logger.log(VERBOSE, f"{self.pfx} out of grow_chains, \n{spc50}in={indict}\n{spc50}wd={grown_working_dict}")

        parsed_working_dict = self.parse_chains(grown_working_dict)
        logger.log(VERBOSE, f"{self.pfx} parsed, \n{spc50}in={grown_working_dict}\n{spc50}out={parsed_working_dict}")

        return parsed_working_dict

    def grow_chains(self, old_working_dict, loop_count):
        """For all the chains of letters in the working_dict, grow the chain by one letter, for each letter
        that the end is connected to. This may fork to create multiple chains from one original."""
        new_working_dict = deepcopy(old_working_dict)

        for iD, chain in old_working_dict.items():
            chain_end = chain[-1]
            chars_chain_end_links_to = self.link_index[chain_end]
            logger.log(SPAM, f"{self.pfx} chain={iD, chain} | end ({chain_end}) links to {chars_chain_end_links_to}")

            for position_iD, conxn in enumerate(chars_chain_end_links_to.values()):
                # adds fractional float value to new_key, smaller for each iteration, for tracking purposes
                new_key = round(iD + position_iD / 10 ** loop_count, 5)
                logger.log(SPAM, f"{self.pfx} saving key={new_key} = {chain}+{conxn}")
                new_working_dict[new_key] = chain + conxn

        return new_working_dict

    def parse_chains(self, grown_working_dict):
        """This loop parses the results of the chain additions, whether it's found a deadend or loop, or neither
        if neither, chain is added back into the working dict for the next iteration
        """
        parsed_working_dict = {}
        for iD, chain in grown_working_dict.items():
            chain_count = Counter(chain)
            commonest_letter, occurrence_count = chain_count.most_common(1)[0]

            if occurrence_count == 1:  # just keep growing to see where it goes
                logger.log(SPAM, f"{self.pfx} keep going for {chain}")
                parsed_working_dict[iD] = chain

            elif occurrence_count == 2:
                if commonest_letter == chain[-1] == chain[-3]:
                    logger.log(SPAM, f"{self.pfx} {chain} is a deadend")
                    self.dead_ends[iD] = chain[:-1]
                elif len(chain) > 3:  # ie we're legit back to the start after a loop
                    self.add_to_found_loops(chain, commonest_letter)
            else:
                raise ValueError(f"error parsing chain = {chain}, too many repeated characters")

        return parsed_working_dict

    def add_to_found_loops(self, new_loop: str, commonest_letter: str) -> None:
        """Makes sure candidate new loop is genuinely new. Selects only the portion of the chain representing the loop
         through a cycle of characters. This loop is converted to a frozenset for comparison against existing found
         loops, and for use as the key in dictionary of found_loops"""
        # e.g. turns EINTON --> NTON, with knowledge that second occurrence of commonest letter will be at the end
        only_loop_section = new_loop[new_loop.index(commonest_letter):]
        new_loop_set = frozenset(only_loop_section)

        already_found = False
        for found_loop in self.found_loops.keys():
            if found_loop.issubset(new_loop_set):
                already_found = True
            elif new_loop_set.issubset(found_loop):
                logger.log(VERBOSE, f"{self.pfx} previously found loop {found_loop} to be replaced by {new_loop_set}")
                del self.found_loops[found_loop]

        if not already_found:
            self.found_loops[new_loop_set] = only_loop_section
            logger.debug(f"{self.pfx} loop found = {only_loop_section}")

    def rationalise_to_list(self, indict):
        """goes through list values of results from find_loops, turns into single large list,
        gets rid of any elements that are mirror images of each other (keeping one unique)"""
        # logger.log(SPAM, f"rationalising {indict}")
        invals = list(set(indict.values()))
        # logger.log(SPAM, f"invals = {invals}")
        for i, loop in enumerate(invals):
            test = deepcopy(invals)
            # logger.log(SPAM, f"setting pos {i} to {loop[::-1]}")
            test[i] = loop[::-1]
            test = list(set(test))
            # logger.log(SPAM, f"test is now {test}")
            if len(test) != len(invals):
                invals[i] = loop[::-1]
                # logger.log(SPAM, f"lens unequal")
        invals = list(set(invals))
        # logger.log(SPAM, f"invals is now {invals}")
        return invals

    def unsub_list(self, inlist):
        """when given a list of strings from rationalise_to_list, will get rid of any elements which are a
        subset of another larger element, leaving only the unique strings"""
        inlist.sort()
        # logger.log(SPAM, f"into unsub= {inlist}")
        unique = []
        for i in range(len(inlist) - 1):
            chain = inlist[i]
            nxt_chain = inlist[i + 1]
            if chain not in nxt_chain:
                unique.append(chain)
                # logger.log(SPAM, f"{chain} NOT in {nxt_chain}")
            # else:
                # logger.log(SPAM, f"{chain} IS  in {nxt_chain}")
        unique.append(inlist[-1])
        # logger.log(SPAM, f"out of unsub= {unique}")
        return unique

    def get_smallest_loop(self, inlist):
        """like unsub list but in reverse, for loops"""
        inlist = sorted(inlist, reverse=True)
        logger.log(SPAM, f"into get_smallest_loop= {inlist}")
        dropped = []
        unique = deepcopy(inlist)
        for chain in inlist:
            for other_chain in inlist:
                if len(chain) < len(other_chain):
                    smaller = chain
                    bigger = other_chain
                else:
                    smaller = other_chain
                    bigger = chain
                test = ((smaller in bigger) or (smaller[::-1] in bigger))
                if smaller == bigger:
                    test = False
                # logger.log(SPAM, (smaller, bigger, test))
                if test and bigger in unique and smaller in unique:
                    dropped.append(bigger)
                    unique.remove(bigger)
                    # logger.log(VERBOSE, f'removed {bigger}')
        logger.log(SPAM, f"dropped  = {dropped}")
        logger.log(SPAM, f"out of get_smallest_loop= {unique}")
        return unique

    def lose_redundant_deadends(self):
        """should be applied after dead ends have been rationalised and unsubbed"""
        check_against_these_loops = set(self.found_loops)
        final_uniq_dends = deepcopy(self.dead_ends)
        dropped = []
        for uchain in self.dead_ends:
            for eachloop in check_against_these_loops:
                if uchain in final_uniq_dends and (
                        uchain in eachloop
                        or uchain[::-1] in eachloop
                        or eachloop in uchain
                        or eachloop[::-1] in uchain
                ):
                    dropped.append(uchain)
                    # logger.log(SPAM, f"dropping {uchain} as related to {eachloop}")
                    final_uniq_dends.remove(uchain)
        logger.log(SPAM, f"dropped deadends = {dropped}")
        self.dead_ends = final_uniq_dends

    def loop_to_menu(self, mainloop=0):
        if mainloop == 0:
            mainloop = self.found_loops[0]

        for i, char in enumerate(mainloop[:-1]):
            next_char = mainloop[i + 1]
            wdict = self.link_index[char]
            position = [k for k, v in wdict.items() if v == next_char][0]
            # note that I'm just picking the first one where there are double (or more) linkages
            # not sure if this matters for now or if its better to somehow include both linkages in the menu
            # revisit later depending on bombe methodology
            self.menu[position] = {'in': char, 'out': next_char, 'menu_link': position}
            print(f"added item from loop '{mainloop}' to menu {position} : {self.menu[position]}")

    def add_deadends_to_menu(self, length_of_menu=12):
        for ends in sorted(self.dead_ends, reverse=True):
            # current_len = len(self.menu)
            #     print(current_len)
            for i, char in enumerate(ends[:-1]):
                if len(self.menu) >= length_of_menu:
                    pass
                else:
                    next_char = ends[i + 1]
                    #         print(i,char,next_char)
                    wdict = self.link_index[char]
                    position = [k for k, v in wdict.items() if v == next_char][0]
                    self.menu[position] = {'in': char, 'out': next_char, 'menu_link': position}
                    logger.debug(f"added item from deadend '{ends}' to menu {position} : {self.menu[position]}")

    def configure_menu(self):
        try:
            test_char = self.found_loops[0][0]
        except BaseException:
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

    def prep_menu(self, length_of_menu=12):
        self.menu = {}
        try:
            for loop in self.found_loops:
                self.loop_to_menu(mainloop=loop)
        except BaseException:
            pass
        self.add_deadends_to_menu(length_of_menu=length_of_menu)
        self.configure_menu()
        self.connections_add_to_menu()

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
