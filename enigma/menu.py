from collections import defaultdict
from copy import deepcopy
from typing import Dict, List

import matplotlib.pyplot as plt
import networkx as nx

from enigma.design import ENTRY
from enigma.utils import SPAM, VERBOSE, get_logger

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
        self.found_loops: Dict = {}
        self.dead_ends: Dict = {}

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
            logger.log(SPAM, f"index of links for char={character} is {link_idx}")
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
        working_dict = {i + 0.0: starting_character for i in range(len(self.link_index[starting_character]))}
        logger.log(SPAM, f"working dict = {working_dict}")
        for i, v in enumerate(self.link_index[starting_character].values()):
            working_dict[i] += v
        logger.log(SPAM, f"working dict is now = {working_dict}")
        run = 1
        tracker = len(self.found_loops)
        while len(working_dict) > 0:
            # with each iteration, size of chains grows by one each time, only keep those that are neither
            # loops or deadends
            working_dict, self.found_loops, self.dead_ends = self.make_connections(
                starting_character, working_dict, self.found_loops, self.dead_ends, run, tracker
            )
            logger.log(SPAM, f"itr={run} | working dict is now = {working_dict}")
            run += 1

    def make_connections(
            self, starting_character: str, indict: Dict, loops: Dict, deadends: Dict, itr: int, tracking_len: int
    ):
        """for sorting through a hipairs dictionary of letters of interest and their corresponding paired letters.
        Used with a WHILE loop, can recursively search through 'chains' or paths that a letter sequence can take
        by following pairs from one letter to the next. Looks for 'loops', where a chain path can return to its original
        starting letter. Records other chains as deadends
        """
        if itr == 1:
            working_dict = {k + tracking_len: v for k, v in deepcopy(indict).items()}
            indict = deepcopy(working_dict)
            logger.log(VERBOSE, f"itr={itr} | working dict with tracking is now {working_dict}")
        else:
            working_dict = deepcopy(indict)

        for iD, chain in indict.items():
            # this loop extends out each chain, by one more character, creating more chains if there is a fork?
            logger.log(SPAM, f"itr={itr} | id-chain = {iD, chain}")
            current_end = chain[-1]
            letters_that_current_end_is_connected_to = self.link_index[current_end]
            logger.log(
                SPAM,
                f"itr={itr} | current end ({current_end}) is connected to {letters_that_current_end_is_connected_to}")
            for jid, conxn in enumerate(letters_that_current_end_is_connected_to.values()):
                key = round(iD + jid / 10 ** itr, 5)
                logger.log(SPAM, f"itr={itr} | key={key}, jid={jid}, conxn={conxn}")
                if conxn != current_end:
                    working_dict[key] = indict[iD] + conxn
        logger.log(VERBOSE, f"itr={itr} | chains grown, working dict is {working_dict}")
        dx = {}
        for kid, chain in working_dict.items():
            # this loop parses the results of the chain additions, whether it's found a deadend or loop, or neither
            # if neither, chain is added back into the working dict for the next iteration
            if chain[-1] == chain[-3]:  # and len(v):
                chain = chain[:-1]
                deadends[kid] = chain
                logger.log(SPAM, f"itr={itr} | {chain} is a deadend")
            elif chain[-1] == starting_character and len(chain) > 3:  # ie we're legit back to the start after a loop
                loops[kid] = chain
                logger.log(VERBOSE, f"itr={itr} | loop found = {chain}")
            else:
                dx[kid] = chain
                logger.log(SPAM, f"itr={itr} | keep going for {chain}")
        logger.log(VERBOSE, f"itr={itr} | parsed working dict is {dx}")
        return dx, loops, deadends

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
