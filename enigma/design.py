from dataclasses import dataclass

import matplotlib.colors as mclr

i = 'I'
ii = 'II'
iii = 'III'
iv = 'IV'
v = 'V'
ROTOR_INDEX = (i, ii, iii, iv, v)

ENTRY = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
raw_rotors = {'I': 'EKMFLGDQVZNTOWYHXUSPAIBRCJ', 'II': 'AJDKSIRUXBLHWTMCQGZNPYFVOE',
              'III': 'BDFHJLCPRTXVZNYEIWGAKMUSQO', 'IV': 'ESOVPZJAYQUIRHXLNFTGKDCMWB',
              'V': 'VZBRGITYUPSDNHLXAWMJQOFECK'}
notches = {'I': 'Q', 'II': 'E', 'III': 'V', 'IV': 'J', 'V': 'Z'}


@dataclass
class ROTORS:
    I = 'EKMFLGDQVZNTOWYHXUSPAIBRCJ'
    II = 'AJDKSIRUXBLHWTMCQGZNPYFVOE'
    III = 'BDFHJLCPRTXVZNYEIWGAKMUSQO'
    IV = 'ESOVPZJAYQUIRHXLNFTGKDCMWB'
    V = 'VZBRGITYUPSDNHLXAWMJQOFECK'
    ALL = (I, II, III, IV, V)
    MAP = {i: I, ii: II, iii: III, iv: IV, v: V}


@dataclass
class NOTCHES:
    "Window setting at which the rotor will cause the rotor to its left to step"
    I = "Q"
    II = "E"
    III = "V"
    IV = "J"
    V = "Z"
    ALL = (I, II, III, IV, V)
    MAP = {i: I, ii: II, iii: III, iv: IV, v: V}


# forward rotors is the forward in:out pairings of each rotor as the
# character index of the A-Z ascii alphabet stored in 'entry'
FORWARD_ROTORS = {i: [4, 10, 12, 5, 11, 6, 3, 16, 21, 25, 13, 19, 14, 22, 24, 7, 23, 20, 18, 15, 0, 8, 1, 17, 2, 9],
                  ii: [0, 9, 3, 10, 18, 8, 17, 20, 23, 1, 11, 7, 22, 19, 12, 2, 16, 6, 25, 13, 15, 24, 5, 21, 14, 4],
                  iii: [1, 3, 5, 7, 9, 11, 2, 15, 17, 19, 23, 21, 25, 13, 24, 4, 8, 22, 6, 0, 10, 12, 20, 18, 16, 14],
                  iv: [4, 18, 14, 21, 15, 25, 9, 0, 24, 16, 20, 8, 17, 7, 23, 11, 13, 5, 19, 6, 10, 3, 2, 12, 22, 1],
                  v: [21, 25, 1, 17, 6, 8, 19, 24, 20, 15, 18, 3, 13, 7, 11, 23, 0, 22, 12, 9, 16, 14, 5, 4, 2, 10]}

# ## reverse rotors - the in:out pairing for when the current flows back from the reflector to the final output.
REVERSE_ROTORS = {i: [20, 22, 24, 6, 0, 3, 5, 15, 21, 25, 1, 4, 2, 10, 12, 19, 7, 23, 18, 11, 17, 8, 13, 16, 14, 9],
                  ii: [0, 9, 15, 2, 25, 22, 17, 11, 5, 1, 3, 10, 14, 19, 24, 20, 16, 6, 4, 13, 7, 23, 12, 8, 21, 18],
                  iii: [19, 0, 6, 1, 15, 2, 18, 3, 16, 4, 20, 5, 21, 13, 25, 7, 24, 8, 23, 9, 22, 11, 17, 10, 14, 12],
                  iv: [7, 25, 22, 21, 0, 17, 19, 13, 11, 6, 20, 15, 23, 16, 2, 4, 9, 12, 1, 18, 10, 3, 24, 14, 8, 5],
                  v: [16, 2, 24, 11, 23, 22, 4, 13, 5, 19, 25, 14, 18, 12, 21, 9, 20, 3, 10, 6, 8, 0, 17, 15, 7, 1]}

# in:out pairings for reflectors
REFLECTORS_CYPHER = {
    'B': {'A': 'Y', 'B': 'R', 'C': 'U', 'D': 'H', 'E': 'Q', 'F': 'S', 'G': 'L', 'H': 'D', 'I': 'P', 'J': 'X', 'K': 'N',
          'L': 'G', 'M': 'O', 'N': 'K', 'O': 'M', 'P': 'I', 'Q': 'E', 'R': 'B', 'S': 'F', 'T': 'Z', 'U': 'C', 'V': 'W',
          'W': 'V', 'X': 'J', 'Y': 'A', 'Z': 'T'},
    'C': {'A': 'F', 'B': 'V', 'C': 'P', 'D': 'J', 'E': 'I', 'F': 'A', 'G': 'O', 'H': 'Y', 'I': 'E', 'J': 'D', 'K': 'R',
          'L': 'Z', 'M': 'X', 'N': 'W', 'O': 'G', 'P': 'C', 'Q': 'T', 'R': 'K', 'S': 'U', 'T': 'Q', 'U': 'S', 'V': 'B',
          'W': 'N', 'X': 'M', 'Y': 'H', 'Z': 'L'}}

# reflectors already turned into integer index positions from letters
REFLECTORS_INDEX = {
    'B': {0: 24, 1: 17, 2: 20, 3: 7, 4: 16, 5: 18, 6: 11, 7: 3, 8: 15, 9: 23, 10: 13, 11: 6, 12: 14, 13: 10, 14: 12,
          15: 8, 16: 4, 17: 1, 18: 5, 19: 25, 20: 2, 21: 22, 22: 21, 23: 9, 24: 0, 25: 19},
    'C': {0: 5, 1: 21, 2: 15, 3: 9, 4: 8, 5: 0, 6: 14, 7: 24, 8: 4, 9: 3, 10: 17, 11: 25, 12: 23, 13: 22, 14: 6, 15: 2,
          16: 19, 17: 10, 18: 20, 19: 16, 20: 18, 21: 1, 22: 13, 23: 12, 24: 7, 25: 11}
}


blank_status = {char: 0 for char in ENTRY}
iomap = {'in': 'I', 'out': 'O', 'conx_in': 'I', 'conx_out': 'O'}
invsoutmap = {'in': 'O', 'out': 'I'}
grey = mclr.to_rgba('gainsboro', 0.2)
red = mclr.to_rgba('firebrick', 0.9)
orange = mclr.to_rgba('lightsalmon', 0.8)
transparent = mclr.to_rgba('white', alpha=0)
