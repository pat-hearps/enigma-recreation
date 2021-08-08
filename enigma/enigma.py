from string import ascii_uppercase
from copy import deepcopy
from typing import List, Dict
import os

import networkx as nx
import matplotlib.pyplot as plt

from enigma.design import (ENTRY, raw_rotors, FORWARD_ROTORS, REVERSE_ROTORS, REFLECTORS_CYPHER, ROTOR_INDEX, ROTORS,
                           NOTCHES, REFLECTORS_INDEX)


def vprint(message: str, msg_level: int, v_level: int = None):
    if v_level is None:
        v_level = int(os.getenv("verbosity", default="0"))
    if msg_level <= v_level:
        print(message)


class Reflector:
    def __init__(self, reflector_type: str):
        assert reflector_type in REFLECTORS_INDEX.keys()
        self.reflector_type: str = reflector_type
        self.cypher: str = REFLECTORS_CYPHER[reflector_type]
        self.index_cypher_forward: int = REFLECTORS_INDEX[reflector_type]


class Rotor:

    def __init__(self, rotor_type: str, window_letter: str = "A", ring_setting: str = "A"):
        assert rotor_type in ROTOR_INDEX
        self.rotor_type: str = rotor_type
        self.cypher: str = ROTORS.MAP[rotor_type]
        self.notch: str = NOTCHES.MAP[rotor_type]
        self.index_cypher_forward: List[int] = FORWARD_ROTORS[rotor_type]
        self.index_cypher_reverse: List[int] = REVERSE_ROTORS[rotor_type]
        # these given letters are how the settings would be set physically
        self.window_letter: str = window_letter
        self.ring_setting: str = ring_setting
        # and are converted into numerical indexes
        self.window_position: int = ENTRY.index(self.window_letter)
        self.ring_position: int = ENTRY.index(self.ring_setting)
        self.update_cypher_position()

    def update_cypher_position(self):
        self.actual_cypher_position: int = (26 + self.window_position - self.ring_position) % 26

    def set_window_letter(self, window_letter: str):
        self.window_letter = window_letter
        self.window_position = ENTRY.index(self.window_letter)
        self.update_cypher_position()

    def step_rotor(self):
        self.window_position = (self.window_position + 1) % 26
        self.window_letter = ENTRY[self.window_position]
        self.update_cypher_position()


class Enigma:
    def __init__(self, left_rotor_type: str, middle_rotor_type: str, right_rotor_type: str, reflector_type: str,
                 current_window_3: str = "AAA", ring_settings_3: str = "AAA"):
        """rotors must be strings referring to either ['I','II','III','IV','V']
        reflector must be string, one of either ['B','C'],
        current_window_3 = initial position of the 3 rotors as defined by the letter visible in the window for each
        ring_settings_3 = display-vs-cypher offset of the rotor, does not change during an operation"""
        assert all([r in raw_rotors.keys() for r in (left_rotor_type, middle_rotor_type, right_rotor_type)])
        assert reflector_type in REFLECTORS_CYPHER.keys()

        self.reflector: Reflector = Reflector(reflector_type=reflector_type)
        self.left_rotor: Rotor = Rotor(rotor_type=left_rotor_type, ring_setting=ring_settings_3[0])
        self.middle_rotor: Rotor = Rotor(rotor_type=middle_rotor_type, ring_setting=ring_settings_3[1])
        self.right_rotor: Rotor = Rotor(rotor_type=right_rotor_type, ring_setting=ring_settings_3[2])

        self.set_window_letters(current_window_3=current_window_3)
        self.in_status: Dict = {char: 0 for char in ENTRY}
        self.out_status: Dict = {char: 0 for char in ENTRY}
        self.record: Dict = {}

    def set_window_letters(self, current_window_3: str):
        """Given a three-letter menu link (e.g. 'ZAB'), set the current positions of the enigma to correspond to the menu link"""
        assert all([m in ascii_uppercase for m in current_window_3])
        assert len(current_window_3) == 3
        current_window_3 = current_window_3.upper()
        self.left_rotor.set_window_letter(current_window_3[0])
        self.middle_rotor.set_window_letter(current_window_3[1])
        self.right_rotor.set_window_letter(current_window_3[2])

        self.window_letters: str = current_window_3

    def update_window_letters(self):
        """Update the enigma's class attribute 'window_letters' to reflect the positions of the rotors"""
        self.window_letters = "".join([r.window_letter for r in (self.left_rotor, self.middle_rotor, self.right_rotor)])

    def step_enigma(self):
        """Step the 3 rotors, as occurs when a key is depressed
        - right rotor is always stepped
        - middle rotor steps if right rotor has reached its notch point
        - left rotor steps if middle rotor has reached its notch point. If this occurs, the middle rotor also steps,
        due to 'double-stepping' of pawl/teeth mechanism.
        Note that notches are not affected by ring position, as the notch is on the moveable outer ring. Rotor will
        always step it's adjacent rotor if its window is displaying it's notch letter."""
        vprint(f"enigma position before stepping={self.window_letters}", 1)

        vprint(f"middle rotor notch={self.middle_rotor.notch}", 2)
        if self.middle_rotor.notch == self.middle_rotor.window_letter:
            vprint("stepping left rotor", 2)
            self.left_rotor.step_rotor()
            vprint("stepping middle rotor with left rotor", 2)
            self.middle_rotor.step_rotor()

        vprint(f"right rotor notch={self.right_rotor.notch}", 2)
        if self.right_rotor.notch == self.right_rotor.window_letter:
            vprint("stepping middle rotor", 2)
            self.middle_rotor.step_rotor()

        vprint("stepping right rotor", 2)
        self.right_rotor.step_rotor()
        self.update_window_letters()
        vprint(f"enigma position after stepping={self.window_letters}", 1)

    def cypher(self, letters: str):
        """
        Cypher (encode or decode) a sequence of characters through the Enigma.
        Loops through what occurs as one letter on the enigma keyboard is pressed:
        1. Enigma rotors are stepped *first*
        2. Signal is sent from the depressed key through the enigma to encode its cypher letter"""
        cypher = ""
        for letter in letters:
            self.step_enigma()
            cypher += full_scramble(self, letter)
        return cypher


def full_scramble(enigma: Enigma, letter_in: str) -> str:

    letter_forward_scrambled = once_thru_scramble(start_character=letter_in,
                                                  forward=True,
                                                  left_rotor=enigma.left_rotor,
                                                  middle_rotor=enigma.middle_rotor,
                                                  right_rotor=enigma.right_rotor)

    position_into_reflector = ENTRY.index(letter_forward_scrambled)
    position_reflected = encode_thru_reflector(reflector=enigma.reflector, entry_position=position_into_reflector)
    letter_reflected = ENTRY[position_reflected]

    letter_reverse_scrambled = once_thru_scramble(start_character=letter_reflected,
                                                  forward=False,
                                                  left_rotor=enigma.left_rotor,
                                                  middle_rotor=enigma.middle_rotor,
                                                  right_rotor=enigma.right_rotor)
    return letter_reverse_scrambled


def once_thru_scramble(start_character: str, forward: bool, left_rotor: Rotor, middle_rotor: Rotor,
                       right_rotor: Rotor) -> str:
    """ start_character must be single ASCII character A-Z"""
    entry_pos = ENTRY.index(start_character.upper())

    if forward:
        first_rotor, third_rotor = right_rotor, left_rotor
    else:
        first_rotor, third_rotor = left_rotor, right_rotor

    rotor_1_out = encode_thru_rotor(first_rotor, entry_position=entry_pos, forward=forward)
    rotor_2_out = encode_thru_rotor(middle_rotor, entry_position=rotor_1_out, forward=forward)
    rotor_3_out = encode_thru_rotor(third_rotor, entry_position=rotor_2_out, forward=forward)

    return ENTRY[rotor_3_out]


def encode_thru_reflector(reflector: Reflector, entry_position: int) -> int:
    vprint(f"---- Rotor type {reflector.reflector_type} ----", 2)
    vprint(f"signal into reflector at position {entry_position}   = {ENTRY[entry_position]}", 1)
    position_out = reflector.index_cypher_forward[entry_position]
    vprint(f"signal out of reflector at position {position_out} = {ENTRY[position_out]}", 1)
    return position_out


def encode_thru_rotor(rotor: Rotor, entry_position: int, forward: bool = True) -> int:
    """Encode signal through a given rotor in either direction.
    state of given Rotor class instance should define the current settings / position etc.
    - entry_position = 0-25 index at which signal is entering, relative to the 'A' position of
    the fixed 'entry' or 'reflector' where signal would be coming from"""
    vprint(f"---- Rotor type {rotor.rotor_type} / window {rotor.window_letter} / ring {rotor.ring_setting} ----", 2)
    vprint(f"signal into rotor at position {entry_position} =       {ENTRY[entry_position]}", 1)
    index_cypher = rotor.index_cypher_forward if forward else rotor.index_cypher_reverse
    # which letter on the cypher rotor the signal is entering at - offset based on rotor step and ring setting
    cypher_in = (entry_position + rotor.actual_cypher_position) % 26
    vprint(f"signal into cypher wiring at letter =    {ENTRY[cypher_in]}", 1)
    # cypher_out from cypher_in is the actual enigma internal wiring encoding
    cypher_out = index_cypher[cypher_in]
    vprint(f"signal encoded out of cypher at letter = {ENTRY[cypher_out]}", 1)
    # where the signal will exit at, offset due same reasons as cypher_in
    position_out = (26 + cypher_out - rotor.actual_cypher_position) % 26
    vprint(f"signal out of rotor at position {position_out} =      {ENTRY[position_out]}", 1)
    return position_out


class MenuMaker:

    def __init__(self, crib, encoded_crib):
        self.crib = crib
        self.encoded_crib = encoded_crib

    def do_pairs(self):
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
