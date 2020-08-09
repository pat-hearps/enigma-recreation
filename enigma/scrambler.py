import random
from string import ascii_uppercase, ascii_letters
from pprint import pprint
from copy import deepcopy
import dill
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mclr

class Scrambler:
    """A Scrambler is a slightly adapted ENIGMA cypher, such that it has both an in and out end which are separate"""
    
    def __init__(self,left_rotor,middle_rotor,right_rotor,reflector,menu_link='ZZZ',conx_in={},conx_out={}):
        """rotors must be strings referring to either ['I','II','III','IV','V']
        reflector must be string, one of either ['B','C']"""
        
        self.right_rotor = right_rotor
        self.middle_rotor = middle_rotor
        self.left_rotor = left_rotor
        self.reflector = reflectors[reflector]
        self.menu_link = menu_link
        self.middle_notch = entry.index(notches[self.middle_rotor])   ## point if right rotor reaches will trigger middle rotor to step
        self.left_notch = entry.index(notches[self.left_rotor])  ## point if middle rotor reaches will trigger left rotor to step
        self.current_position = menu_link
        self.pos_left_rotor, self.pos_mid_rotor, self.pos_rgt_rotor = (ascii_uppercase.index(m) for m in menu_link.upper())
        self.status = {}
        self.status['in'] = {char:0 for char in entry}
        self.status['out'] = {char:0 for char in entry}
        self.conxns = {'in':conx_in, 'out':conx_out}
        
    def once_thru_scramble(self,start_character, direction, first_rotor, pos1, second_rotor, pos2, 
                       third_rotor, pos3):
        """ start_character must be single ASCII character A-Z
        direction is either 'forward' or 'back' """
        if direction == 'forward':
            usedict = {k:v for k,v in forward_rotors.items()}
        elif direction == 'back':
            usedict = {k:v for k,v in rev_rotors.items()}
        else:
            print('only forward or back for direction')
            return 'wtf'

        start_character = start_character.upper()
        entry_pos = entry.index(start_character)
        fst_pos_modifier = (26 + pos1 - 0)%26
        fst_in = (entry_pos + fst_pos_modifier)%26
        fst_out = usedict[first_rotor][fst_in]
        ch1o = entry[fst_out]

        scd_pos_modifier = (26 + pos2 - pos1)%26
        scd_in = (fst_out + scd_pos_modifier)%26
        ch2i = entry[scd_in]
        scd_out = usedict[second_rotor][scd_in]
        ch2o = entry[scd_out]

        thd_pos_modifier = (26 + pos3 - pos2)%26
        thd_in = (scd_out + thd_pos_modifier)%26
        ch3i = entry[thd_in]
        thd_out = usedict[third_rotor][thd_in]
        ch3o = entry[thd_out]
        return ch3o
    
    def full_scramble(self,in_ch):
        in_ch = in_ch.upper()
        left_rotor = self.left_rotor
        middle_rotor = self.middle_rotor
        right_rotor = self.right_rotor
        rflector = self.reflector
        ## first run right to left through scrambler
        forward_run = self.once_thru_scramble(in_ch, direction='forward', first_rotor=right_rotor, pos1=self.pos_rgt_rotor, 
                                              second_rotor=middle_rotor, pos2=self.pos_mid_rotor, 
                                              third_rotor=left_rotor, pos3=self.pos_left_rotor)
        ## reflector back around for return
        rfi_pos_mod = (26 + 0 - self.pos_left_rotor)%26    ## the '0' is there to matching formatting of other position modifiers - reflector is not moved so it will always be 0
        rf_in = (entry.index(forward_run) + rfi_pos_mod)%26
        chri = entry[rf_in]
        mirrored = rflector[chri]

        ## second run back left to right thru scrambler
        back_run = self.once_thru_scramble(mirrored, direction='back', first_rotor=left_rotor, pos1=self.pos_left_rotor, 
                                      second_rotor=middle_rotor, pos2=self.pos_mid_rotor, third_rotor=right_rotor, pos3=self.pos_rgt_rotor)
        bk_out = entry.index(back_run)
        bko_pos_mod = (26 + 0 - self.pos_rgt_rotor)%26  ## as above, '0' just reflects that the entry interface doesn't move
        bk_final = (bk_out + bko_pos_mod)%26
        final = entry[bk_final]
        return final
    
    def rotor_step(self,rotor_position):
        """To be used on any single rotor. Steps forward one position, resetting back to 0 after it reaches 25"""
        if rotor_position == 25:
            rotor_position = 0
        else:
            rotor_position += 1
        return rotor_position
    
    def translate_current_position(self):
        """Reads the numerical position of each of the 3 rotors, and translates into ZZA-style alphabet position
        That is, for each of the three rotors, it's numerical position from 0-25 is mapped to the letter of the 
        alphabet this corresponds to. Note that this is purely for displaying the setting to the user, it can't 
        do anything to alter the actual rotor position, which is stored as the numerical variable"""
        self.current_position = ''
        for pos in self.pos_left_rotor,self.pos_mid_rotor,self.pos_rgt_rotor:
            self.current_position += entry[pos]
    
    def step_enigma(self):
        """Just acts on itself, steps all three rotors, stepping either 1,2 or 3 rotors based on the 
        notch position"""
        if self.pos_rgt_rotor == self.middle_notch and self.pos_mid_rotor == self.left_notch:
            self.pos_rgt_rotor = self.rotor_step(self.pos_rgt_rotor)
            self.pos_mid_rotor = self.rotor_step(self.pos_mid_rotor)
            self.pos_left_rotor = self.rotor_step(self.pos_left_rotor)
        elif self.pos_rgt_rotor == self.middle_notch:
            self.pos_rgt_rotor = self.rotor_step(self.pos_rgt_rotor)
            self.pos_mid_rotor = self.rotor_step(self.pos_mid_rotor)
        else:
            self.pos_rgt_rotor = self.rotor_step(self.pos_rgt_rotor)        
        self.translate_current_position()           

    def update(self):
        """idea here is that the scrambler will check each of the 26 connections to see if they
        are live, and if so pass it through itself to light up the corresponding scramble (i.e. encyphered) 
        character on the other side of  the scrambler"""
        for sides in [['in','out'],['out','in']]:
            for char, io in self.status[sides[0]].items():
                if io == 0:
                    pass
                else:
                    self.status[sides[1]][self.full_scramble(char)] = 1
                    
    def reset_status(self):
        """As it says on box, resets the status (dictionary of A-Z and 1/0 for each) all back to 0"""
        self.status['in'] = {char:0 for char in entry}
        self.status['out'] = {char:0 for char in entry}
