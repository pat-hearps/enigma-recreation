from copy import deepcopy

import networkx as nx
import matplotlib.pyplot as plt

from enigma.design import ENTRY
from enigma.utils import get_logger

logger = get_logger(__name__)

class MenuMaker:

    def __init__(self, crib, encoded_crib):
        self.crib = crib
        self.encoded_crib = encoded_crib

    def do_pairs(self):
        logger.debug("doing pairs")
        self.pairs = {i: {c, m} for i, c, m in zip(range(len(self.crib)), self.crib, self.encoded_crib)}
        self.links = {character: len([pair for pair in self.pairs.values() if character in pair]) for character in
                      ENTRY}
        self.hilinks = {k: v for k, v in self.links.items() if v > 0}
        # ## actually think I should make hilinks just a ranked(sorted) list of characters from highest to lowest
        self.mostlinks = sorted(self.hilinks.values(), reverse=True)[0]
        self.best_characters = [k for k, v in self.hilinks.items() if v == self.mostlinks]

        self.hipairs = {}
        for character in self.hilinks.keys():
            hset = {k: list(pair) for k, pair in self.pairs.items() if character in pair}
            newresult = {}
            for k, v in hset.items():
                v.remove(character)
                if v[0] in self.hilinks.keys():
                    newresult[k] = v[0]
            if len(newresult) > 0:
                self.hipairs[character] = newresult
        logger.debug(f"hipairs are: {self.hipairs}")
        #     hipairs[character] = {k:pair.remove(character) for k,pair in pairs.items() if character in pair}
        # # maybe try a comprehension again later, involves a few steps...

    def make_connections(self, starting_character, indict, loops={}, deadends={}, itr=1, tracking_len=0):
        """for sorting through a hipairs dictionary of letters of interest and their corresponding paired letters.
        Used with a WHILE loop, can recursively search through 'chains' or paths that a letter sequence can take
        by following pairs from one letter to the next. Looks for 'loops', where a chain path can return to its original
        starting letter. Records other chains as deadends
        """
        if itr == 1:
            working_dict = {k + tracking_len: v for k, v in deepcopy(indict).items()}
            indict = deepcopy(working_dict)
        else:
            working_dict = deepcopy(indict)

        for iD, chain in indict.items():

            current_end = chain[-1]
            letters_that_current_end_is_connected_to = self.hipairs[current_end]
            for jid, conxn in enumerate(letters_that_current_end_is_connected_to.values()):
                key = round(iD + jid / 10 ** itr, 5)

                if conxn != current_end:
                    working_dict[key] = indict[iD] + conxn

        dx = {}
        for kid, chain in working_dict.items():
            if chain[-1] == chain[-3]:  # and len(v):
                chain = chain[:-1]
                deadends[kid] = chain
            elif chain[-1] == starting_character and len(chain) > 3:  ## ie we're legit back to the start after a loop
                loops[kid] = chain
            else:
                dx[kid] = chain
        return dx, loops, deadends

    def find_loops(self, starting_character):
        logger.debug(f"finding loops for {starting_character}")
        working_dict = {i + 0.0: starting_character for i in range(len(self.hipairs[starting_character]))}
        for i, v in zip(range(len(self.hipairs[starting_character])), self.hipairs[starting_character].values()):
            working_dict[i] += v

        run = 1
        tracker = len(self.found_loops)
        while len(working_dict) > 0:
            working_dict, self.found_loops, self.dead_ends = self.make_connections(starting_character, working_dict,
                                                                                   self.found_loops, self.dead_ends,
                                                                                   run, tracker)
            run += 1

    def rationalise_to_list(self, indict):
        """goes through list values of results from find_loops, turns into single large list,
        gets rid of any elements that are mirror images of each other (keeping one unique)"""
        invals = list(set(indict.values()))
        for i, loop in enumerate(invals):
            test = deepcopy(invals)
            test[i] = loop[::-1]
            test = list(set(test))
            if len(test) != len(invals):
                invals[i] = loop[::-1]
        invals = list(set(invals))

        return invals

    def unsub_list(self, inlist):
        """when given a list of strings from rationalise_to_list, will get rid of any elements which are a
        subset of another larger element, leaving only the unique strings"""
        inlist.sort()
        unique = []
        for i in range(len(inlist) - 1):
            chain = inlist[i]
            nxt_chain = inlist[i + 1]
            if chain not in nxt_chain:
                unique.append(chain)
        unique.append(inlist[-1])

        return unique

    def get_smallest_loop(self, inlist):
        """like unsub list but in reverse, for loops"""
        inlist = sorted(inlist, reverse=True)
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
                print(smaller, bigger, test)
                if test and bigger in unique and smaller in unique:
                    unique.remove(bigger)
                    print('removed', bigger)
                    print(unique)

        return unique

    def lose_redundant_deadends(self):
        """should be applied after dead ends have been rationalised and unsubbed"""
        check_against_these_loops = set(self.found_loops)
        final_uniq_dends = deepcopy(self.dead_ends)
        for uchain in self.dead_ends:
            for eachloop in check_against_these_loops:
                if (uchain in eachloop or uchain[::-1] in eachloop or eachloop in uchain or eachloop[
                                                                                            ::-1] in uchain) and uchain in final_uniq_dends:
                    final_uniq_dends.remove(uchain)

        self.dead_ends = final_uniq_dends

    def process_stuff(self):
        self.do_pairs()
        self.found_loops = {}
        self.dead_ends = {}
        for char in self.best_characters:
            #             print('############ run for ',char)
            self.find_loops(char)
        self.dead_ends = self.rationalise_to_list(self.dead_ends)
        print('dends b4', self.dead_ends)
        self.dead_ends = self.unsub_list(self.dead_ends)
        print('dends after', self.dead_ends)
        self.found_loops = self.rationalise_to_list(self.found_loops)
        print('loops b4', self.found_loops)
        self.found_loops = self.get_smallest_loop(self.found_loops)
        print('loops after', self.found_loops)
        self.lose_redundant_deadends()

    def loop_to_menu(self, mainloop=0):
        if mainloop == 0:
            mainloop = self.found_loops[0]

        for i, char in enumerate(mainloop[:-1]):
            next_char = mainloop[i + 1]
            wdict = self.hipairs[char]
            position = [k for k, v in wdict.items() if v == next_char][0]
            ### note that I'm just picking the first one where there are double (or more) linkages
            ### not sure if this matters for now or if its better to somehow include both linkages in the menu
            ### revisit later depending on bombe methodology
            self.menu[position] = {'in': char, 'out': next_char, 'menu_link': position}
            print(f"added item from loop '{mainloop}' to menu {position} : {self.menu[position]}")

    def add_deadends_to_menu(self, length_of_menu=12):
        for ends in sorted(self.dead_ends, reverse=True):
            current_len = len(self.menu)
            #     print(current_len)
            for i, char in enumerate(ends[:-1]):
                if len(self.menu) >= length_of_menu:
                    pass
                else:
                    next_char = ends[i + 1]
                    #         print(i,char,next_char)
                    wdict = self.hipairs[char]
                    position = [k for k, v in wdict.items() if v == next_char][0]
                    self.menu[position] = {'in': char, 'out': next_char, 'menu_link': position}
                    print(f"added item from deadend '{ends}' to menu {position} : {self.menu[position]}")

    def configure_menu(self):
        try:
            test_char = self.found_loops[0][0]
        except:
            dend_string = "".join(m for m in self.dead_ends)
            count_of_dead_ends = {}
            for d in dend_string:
                if d not in count_of_dead_ends.keys():
                    count_of_dead_ends[d] = 1
                else:
                    count_of_dead_ends[d] += 1

            test_char = \
            [k for k, v in count_of_dead_ends.items() if v == sorted(count_of_dead_ends.values(), reverse=True)[0]][0]

        self.menu['config'] = {}
        self.menu['config']['test_char'] = test_char
        self.menu['config']['menu_link'] = 'QQQ'
        self.menu['config']['in'] = test_char
        self.menu['config']['out'] = test_char
        self.menu['config']['conxns'] = {'in': {}, 'out': {}}

    def connections_add_to_menu(self):
        ## this part adds in blank conx_in/out dicts and converts position to menulink 3-letter ZZ code
        for k, m in self.menu.items():
            if k == 'config':
                pass
            else:
                l = m['menu_link']
                l = ENTRY[l - 1]
                l = 'ZZ' + l
                #     print(l)
                self.menu[k]['menu_link'] = l
                self.menu[k]['conxns'] = {'in': {}, 'out': {}}
        #                 self.menu[k]['conx_out'] = {}

        ## this part does the heavy lifting of populating the connections for each menu item
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
        except:
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

        if reset_pos == False:
            pass
        else:
            self.pos = nx.spring_layout(self.MultiGraph, k=0.4, scale=1)

        nx.draw_networkx(self.MultiGraph, pos=self.pos)

        labels = nx.get_edge_attributes(self.MultiGraph, 'label')
        labels = {(k[0], k[1]): v for k, v in
                  labels.items()}  ## doesnt' seem to be able to deal with labels for multiples edges
        edge_labels = nx.draw_networkx_edge_labels(self.MultiGraph, pos=self.pos, edge_labels=labels)
        plt.show(fig)