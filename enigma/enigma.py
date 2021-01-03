from string import ascii_uppercase, ascii_letters
from copy import deepcopy
from typing import List

import networkx as nx
import matplotlib.pyplot as plt

from enigma.design import entry, raw_rotors, forward_rotors, rev_rotors, notches, reflectors, ROTOR_INDEX, ROTORS, \
    NOTCHES


def once_through_scramble(start_character: str, direction: str, first_rotor: str, pos1: int, second_rotor: str, pos2: int,
                           third_rotor: str, pos3: int):
    """ start_character must be single ASCII character A-Z
            direction is either 'forward' or 'back' """
    if direction == 'forward':
        usedict = {k: v for k, v in forward_rotors.items()}
    elif direction == 'back':
        usedict = {k: v for k, v in rev_rotors.items()}
    else:
        print('only forward or back for direction')
        assert False
    # problem is confusion around left/middle/right rotors vs first/second/third rotors and forward/back
    # this currently works as if first = left, middle=second, third = right. If in 'forward'. Is this desired?
    start_character = start_character.upper()
    entry_pos = entry.index(start_character)
    fst_pos_modifier = (26 + pos1 - 0) % 26
    fst_in = (entry_pos + fst_pos_modifier) % 26
    fst_out = usedict[first_rotor][fst_in]
    ch1o = entry[fst_out]

    scd_pos_modifier = (26 + pos2 - pos1) % 26
    scd_in = (fst_out + scd_pos_modifier) % 26
    ch2i = entry[scd_in]
    scd_out = usedict[second_rotor][scd_in]
    ch2o = entry[scd_out]

    thd_pos_modifier = (26 + pos3 - pos2) % 26
    thd_in = (scd_out + thd_pos_modifier) % 26
    ch3i = entry[thd_in]
    thd_out = usedict[third_rotor][thd_in]
    ch3o = entry[thd_out]
    if direction == 'forward':
        print(
            f"{start_character} -> (RR out) {ch1o} -> (MR in) {ch2i} -> (MR out) {ch2o} -> (LR in) {ch3i} -> (LR out) {ch3o}")
    elif direction == 'back':
        print(
            f"{start_character} -> (LR out) {ch1o} -> (MR in) {ch2i} -> (MR out) {ch2o} -> (RR in) {ch3i} -> (RR out) {ch3o}")

    return ch3o


class Rotor:

    def __init__(self, rotor_type: str, window_letter: str = "A", ring_setting: str = "A"):
        assert rotor_type in ROTOR_INDEX
        self.rotor_type: str = rotor_type
        self.cypher: str = ROTORS.MAP[rotor_type]
        self.notch: str = NOTCHES.MAP[rotor_type]
        self.index_cypher_forward: List[int] = forward_rotors[rotor_type]
        self.index_cypher_reverse: List[int] = rev_rotors[rotor_type]
        # these given letters are how the settings would be set physically
        self.window_letter = window_letter
        self.ring_setting = ring_setting
        # and are converted into numerical indexes
        self.window_position = entry.index(self.window_letter)
        self.ring_position = entry.index(self.ring_setting)
        self.actual_cypher_position = (26 + self.window_position - self.ring_position) % 26


def encode_thru_rotor(rotor: Rotor, entry_position: int, forward: bool = True):
    """Encode signal through a given rotor in either direction.
    state of given Rotor class instance should define the current settings / position etc.
    - entry_position = 0-25 index at which signal is entering, relative to the 'A' position of
    the fixed 'entry' or 'reflector' where signal would be coming from"""
    index_cypher = rotor.index_cypher_forward if forward else rotor.index_cypher_reverse
    # which letter on the cypher rotor the signal is entering at - offset based on rotor step and ring setting
    cypher_in = (entry_position + rotor.actual_cypher_position) % 26
    # cypher_out from cypher_in is the actual enigma internal wiring encoding
    cypher_out = index_cypher[cypher_in]
    # where the signal will exit at, offset due same reasons as cypher_in
    position_out = (26 + cypher_out - rotor.actual_cypher_position) % 26
    return position_out


class Enigma3:

    def __init__(self, left_rotor: str, middle_rotor: str, right_rotor: str, reflector: str, menu_link: str = 'ZZZ'):
        """rotors must be strings referring to either ['I','II','III','IV','V']
        reflector must be string, one of either ['B','C'],
        menu_link = initial position of the 3 rotors as defined by the letter visible in the window for each"""
        assert all([r in raw_rotors.keys() for r in (left_rotor, middle_rotor, right_rotor)])
        assert reflector in reflectors.keys()

        self.right_rotor = right_rotor
        self.middle_rotor = middle_rotor
        self.left_rotor = left_rotor
        self.reflector = reflectors[reflector]
        self.menu_link = menu_link
        ## point if right rotor reaches will trigger middle rotor to step
        self.middle_notch = entry.index(notches[self.middle_rotor])
        ## point if middle rotor reaches will trigger left rotor to step
        self.left_notch = entry.index(notches[self.left_rotor])
        self.pos_left_rotor, self.pos_mid_rotor, self.pos_rgt_rotor = (ascii_uppercase.index(m) for m in
                                                                       menu_link.upper())
        self.in_status = {char: 0 for char in entry}
        self.out_status = {char: 0 for char in entry}
        self.current_position = menu_link
        self.record = {}

    def once_thru_scramble(self, start_character, direction, first_rotor, pos1, second_rotor, pos2,
                           third_rotor, pos3):
        """ start_character must be single ASCII character A-Z
        direction is either 'forward' or 'back' """
        if direction == 'forward':
            usedict = {k: v for k, v in forward_rotors.items()}
        elif direction == 'back':
            usedict = {k: v for k, v in rev_rotors.items()}
        else:
            print('only forward or back for direction')
            return 'wtf'
        # problem is confusion around left/middle/right rotors vs first/second/third rotors and forward/back
        # this currently works as if first = left, middle=second, third = right. If in 'forward'. Is this desired?
        start_character = start_character.upper()
        entry_pos = entry.index(start_character)
        fst_pos_modifier = (26 + pos1 - 0) % 26
        fst_in = (entry_pos + fst_pos_modifier) % 26
        fst_out = usedict[first_rotor][fst_in]
        ch1o = entry[fst_out]

        scd_pos_modifier = (26 + pos2 - pos1) % 26
        scd_in = (fst_out + scd_pos_modifier) % 26
        ch2i = entry[scd_in]
        scd_out = usedict[second_rotor][scd_in]
        ch2o = entry[scd_out]

        thd_pos_modifier = (26 + pos3 - pos2) % 26
        thd_in = (scd_out + thd_pos_modifier) % 26
        ch3i = entry[thd_in]
        thd_out = usedict[third_rotor][thd_in]
        ch3o = entry[thd_out]
        if direction == 'forward':
            print(
                f"{start_character} -> (RR out) {ch1o} -> (MR in) {ch2i} -> (MR out) {ch2o} -> (LR in) {ch3i} -> (LR out) {ch3o}")
        elif direction == 'back':
            print(
                f"{start_character} -> (LR out) {ch1o} -> (MR in) {ch2i} -> (MR out) {ch2o} -> (RR in) {ch3i} -> (RR out) {ch3o}")

        return ch3o

    def full_scramble(self, in_ch):
        in_ch = in_ch.upper()
        left_rotor = self.left_rotor
        middle_rotor = self.middle_rotor
        right_rotor = self.right_rotor
        rflector = self.reflector
        # # first run right to left through scrambler
        forward_run = self.once_thru_scramble(in_ch, direction='forward', first_rotor=right_rotor,
                                              pos1=self.pos_rgt_rotor,
                                              second_rotor=middle_rotor, pos2=self.pos_mid_rotor,
                                              third_rotor=left_rotor, pos3=self.pos_left_rotor)

        # # reflector back around for return
        rfi_pos_mod = (
                                  26 + 0 - self.pos_left_rotor) % 26  ## the '0' is there to matching formatting of other position modifiers - reflector is not moved so it will always be 0
        rf_in = (entry.index(forward_run) + rfi_pos_mod) % 26
        chri = entry[rf_in]
        mirrored = rflector[chri]

        #         print(f"{forward_run} -> {chri} (into reflector) -> {mirrored} (reflected out)")

        # # second run back left to right thru scrambler
        back_run = self.once_thru_scramble(mirrored, direction='back', first_rotor=left_rotor, pos1=self.pos_left_rotor,
                                           second_rotor=middle_rotor, pos2=self.pos_mid_rotor, third_rotor=right_rotor,
                                           pos3=self.pos_rgt_rotor)

        bk_out = entry.index(back_run)
        bko_pos_mod = (
                                  26 + 0 - self.pos_rgt_rotor) % 26  ## as above, '0' just reflects that the entry interface doesn't move
        bk_final = (bk_out + bko_pos_mod) % 26
        final = entry[bk_final]
        #         print('RR back out:  ', back_run, '-->', final)
        #         print(in_ch,"-->",final)
        return final

    def rotor_step(self, rotor_position):
        """"""
        if rotor_position == 25:
            rotor_position = 0
        else:
            rotor_position += 1
        return rotor_position

    def set_current_position(self, menu_link):
        """Given a three-letter menu link (e.g. 'ZAB'), set the current positions of the enigma to correspond to the menu link"""
        assert all([m in ascii_uppercase for m in menu_link])
        assert len(menu_link) == 3
        self.pos_left_rotor, self.pos_mid_rotor, self.pos_rgt_rotor = (ascii_uppercase.index(m) for m in
                                                                       menu_link.upper())
        self.current_position = menu_link

    def translate_current_position(self):
        self.current_position = ''
        for pos in self.pos_left_rotor, self.pos_mid_rotor, self.pos_rgt_rotor:
            self.current_position += entry[pos]

    def step_enigma(self):
        """Just acts on itself, steps the rotors"""

        #         print(f"Lpos={self.pos_left_rotor}, Mpos={self.pos_mid_rotor}, Rpos={self.pos_rgt_rotor}")
        if self.pos_rgt_rotor == self.middle_notch and self.pos_mid_rotor == self.left_notch:
            self.pos_rgt_rotor = self.rotor_step(self.pos_rgt_rotor)
            self.pos_mid_rotor = self.rotor_step(self.pos_mid_rotor)
            self.pos_left_rotor = self.rotor_step(self.pos_left_rotor)
        #             print('--- left & middle rotor step')
        elif self.pos_rgt_rotor == self.middle_notch:
            self.pos_rgt_rotor = self.rotor_step(self.pos_rgt_rotor)
            self.pos_mid_rotor = self.rotor_step(self.pos_mid_rotor)
        #             print('--- middle rotor step ---')
        else:
            self.pos_rgt_rotor = self.rotor_step(self.pos_rgt_rotor)
        self.translate_current_position()

    #         print(f"Lpos={self.pos_left_rotor}, Mpos={self.pos_mid_rotor}, Rpos={self.pos_rgt_rotor}")

    def only_ascii(self, instring):
        """strips out anything that's not an ascii character (i.e a-z alphabet character), capitalises"""
        newstring = ''
        for character in instring:
            if character in ascii_letters:
                newstring += character.upper()
        return newstring

    def enigmatise(self, tocode, startset='AAA'):
        encoded = ''

        tocode = self.only_ascii(tocode)

        self.pos_left_rotor, self.pos_mid_rotor, self.pos_rgt_rotor = (ascii_uppercase.index(s) for s in
                                                                       startset.upper())

        for i, c in enumerate(tocode):
            #             print('in:    ', c)
            self.step_enigma()

            #             print('rp = ', self.pos_rgt_rotor, 'mp = ', self.pos_mid_rotor, 'lp = ', self.pos_left_rotor)

            out = self.full_scramble(c)
            #             print('out:   ', out,'\n')

            encoded += out
            self.translate_current_position()
            self.record[i] = {'in': c, 'out': out, 'current_pos': self.current_position}

        return encoded


class MenuMaker:

    def __init__(self, crib, encoded_crib):
        self.crib = crib
        self.encoded_crib = encoded_crib

    def do_pairs(self):
        self.pairs = {i: {c, m} for i, c, m in zip(range(len(self.crib)), self.crib, self.encoded_crib)}
        self.links = {character: len([pair for pair in self.pairs.values() if character in pair]) for character in
                      entry}
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
                l = entry[l - 1]
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
