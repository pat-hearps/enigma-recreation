from string import ascii_uppercase
from typing import Dict, List

from enigma.design import (
    ENTRY,
    FORWARD_ROTORS,
    NOTCHES,
    REFLECTORS_CYPHER,
    REFLECTORS_INDEX,
    REVERSE_ROTORS,
    ROTOR_INDEX,
    ROTORS,
    raw_rotors,
)
from enigma.utils import BARF, SPAM, get_logger

logger = get_logger(__name__)


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


class BaseEnigma:
    def __init__(self, left_rotor_type: str, middle_rotor_type: str, right_rotor_type: str, reflector_type: str,
                 ring_settings_3: str = "AAA", current_window_3: str = "AAA"):
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

    def set_window_letters(self, current_window_3: str):
        """Given a three-letter menu link (e.g. 'ZAB'), set the current positions of the enigma to correspond to the menu link"""
        assert all([m in ascii_uppercase for m in current_window_3])
        assert len(current_window_3) == 3
        current_window_3 = current_window_3.upper()
        self.left_rotor.set_window_letter(current_window_3[0])
        self.middle_rotor.set_window_letter(current_window_3[1])
        self.right_rotor.set_window_letter(current_window_3[2])
        self.translate_window_letters()

    def translate_window_letters(self):
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
        letters_before = self.window_letters

        logger.log(BARF, f"middle rotor notch={self.middle_rotor.notch}")
        if self.middle_rotor.notch == self.middle_rotor.window_letter:
            logger.log(BARF, "stepping left rotor")
            self.left_rotor.step_rotor()
            logger.log(BARF, "stepping middle rotor with left rotor")
            self.middle_rotor.step_rotor()

        logger.log(BARF, f"right rotor notch={self.right_rotor.notch}")
        if self.right_rotor.notch == self.right_rotor.window_letter:
            logger.log(BARF, "stepping middle rotor")
            self.middle_rotor.step_rotor()

        logger.log(BARF, "stepping right rotor")
        self.right_rotor.step_rotor()
        self.translate_window_letters()
        logger.log(SPAM, f"enigma position before stepping={letters_before}, after={self.window_letters}")

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


class Enigma(BaseEnigma):
    def __init__(self, left_rotor_type: str, middle_rotor_type: str, right_rotor_type: str, reflector_type: str,
                 ring_settings_3: str = "AAA", current_window_3: str = "AAA"):
        """"""
        super().__init__(
            left_rotor_type=left_rotor_type,
            middle_rotor_type=middle_rotor_type,
            right_rotor_type=right_rotor_type,
            reflector_type=reflector_type,
            ring_settings_3=ring_settings_3,
            current_window_3=current_window_3)
        self.in_status: Dict = {char: 0 for char in ENTRY}
        self.out_status: Dict = {char: 0 for char in ENTRY}
        self.record: Dict = {}


def full_scramble(enigma: BaseEnigma, letter_in: str) -> str:
    """Encode a character through the full Enigma, from keyboard to cypher board.
    1. Forwards through the 3 Rotors
    2. Through the Reflector
    3. Reverse back through the 3 Rotors"""
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
    """Encode a character through 3 consecutive Rotors, either forwards (from Entry to Reflector) or reverse (Reflector
    to Entry).
    start_character must be single ASCII character A-Z"""
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
    logger.log(BARF, f"---- Rotor type {reflector.reflector_type} ----")
    logger.log(BARF, f"signal into reflector at position {entry_position}   = {ENTRY[entry_position]}")
    position_out = reflector.index_cypher_forward[entry_position]
    logger.log(BARF, f"signal out of reflector at position {position_out} = {ENTRY[position_out]}")
    return position_out


def encode_thru_rotor(rotor: Rotor, entry_position: int, forward: bool = True) -> int:
    """Encode signal through a given rotor in either direction.
    state of given Rotor class instance should define the current settings / position etc.
    - entry_position = 0-25 index at which signal is entering, relative to the 'A' position of
    the fixed 'entry' or 'reflector' where signal would be coming from"""
    logger.log(
        BARF,
        f"---- Rotor type {rotor.rotor_type} / window {rotor.window_letter} / ring {rotor.ring_setting} ----")
    logger.log(BARF, f"signal into rotor at position {entry_position} =       {ENTRY[entry_position]}")
    index_cypher = rotor.index_cypher_forward if forward else rotor.index_cypher_reverse
    # which letter on the cypher rotor the signal is entering at - offset based on rotor step and ring setting
    cypher_in = (entry_position + rotor.actual_cypher_position) % 26
    logger.log(BARF, f"signal into cypher wiring at letter =    {ENTRY[cypher_in]}")
    # cypher_out from cypher_in is the actual enigma internal wiring encoding
    cypher_out = index_cypher[cypher_in]
    logger.log(BARF, f"signal encoded out of cypher at letter = {ENTRY[cypher_out]}")
    # where the signal will exit at, offset due same reasons as cypher_in
    position_out = (26 + cypher_out - rotor.actual_cypher_position) % 26
    logger.log(BARF, f"signal out of rotor at position {position_out} =      {ENTRY[position_out]}")
    return position_out
