from string import ascii_uppercase, ascii_letters
import matplotlib.colors as mclr

entry = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
raw_rotors = {'I': 'EKMFLGDQVZNTOWYHXUSPAIBRCJ', 'II': 'AJDKSIRUXBLHWTMCQGZNPYFVOE', 'III': 'BDFHJLCPRTXVZNYEIWGAKMUSQO', 'IV': 'ESOVPZJAYQUIRHXLNFTGKDCMWB', 'V': 'VZBRGITYUPSDNHLXAWMJQOFECK'}
notches = {'I':'Q','II':'E','III':'V','IV':'J','V':'Z'}

## forward rotors is the forward in:out pairings of each rotor as the character index of the A-Z ascii alphabet stored in 'entry'
forward_rotors = {k:[ascii_uppercase.index(c) for c in raw_rotors[k]] for k in raw_rotors.keys()}

## couldn't see a straightforward list comprehension for the reverse - the in:out pairing for when the current flows
## back from the reflector to the final output. Hopefully this two-step for loop isn't too slow
rev_rotors = {}
for r in raw_rotors.keys():
    working = {k:entry.index(v) for k,v in zip(raw_rotors[r],entry)}
    rev_rotors[r] = [working[k] for k in sorted(working.keys())]


## in:out pairings for reflectors
reflectors = {'B': {'A': 'Y', 'B': 'R', 'C': 'U', 'D': 'H', 'E': 'Q', 'F': 'S', 'G': 'L', 'H': 'D', 'I': 'P', 'J': 'X', 'K': 'N', 'L': 'G', 'M': 'O', 'N': 'K', 'O': 'M', 'P': 'I', 'Q': 'E', 'R': 'B', 'S': 'F', 'T': 'Z', 'U': 'C', 'V': 'W', 'W': 'V', 'X': 'J', 'Y': 'A', 'Z': 'T'}, 
              'C': {'A': 'F', 'B': 'V', 'C': 'P', 'D': 'J', 'E': 'I', 'F': 'A', 'G': 'O', 'H': 'Y', 'I': 'E', 'J': 'D', 'K': 'R', 'L': 'Z', 'M': 'X', 'N': 'W', 'O': 'G', 'P': 'C', 'Q': 'T', 'R': 'K', 'S': 'U', 'T': 'Q', 'U': 'S', 'V': 'B', 'W': 'N', 'X': 'M', 'Y': 'H', 'Z': 'L'}}

blank_status = {char:0 for char in entry}
iomap = {'in':'I', 'out':'O', 'conx_in':'I', 'conx_out':'O'}
invsoutmap = {'in':'O','out':'I'}
grey = mclr.to_rgba('gainsboro',0.2)
red = mclr.to_rgba('firebrick',0.9)
orange = mclr.to_rgba('lightsalmon',0.8)
transparent = mclr.to_rgba('white',alpha=0)