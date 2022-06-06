
from enigma.constants import MENU as M

BASIC_3CH = {
    0: {M.IN: 'B',
        M.OUT: 'A',
        M.LINK: 'ZZZ',
        M.CONXNS: {M.IN: {1: M.OUT, 3: M.IN}, M.OUT: {2: M.IN}}},
    2: {M.IN: 'A',
        M.OUT: 'C',
        M.LINK: 'ZZB',
        M.CONXNS: {M.IN: {0: M.OUT}, M.OUT: {1: M.IN}}},
    1: {M.IN: 'C',
        M.OUT: 'B',
        M.LINK: 'ZZA',
        M.CONXNS: {M.IN: {2: M.OUT}, M.OUT: {0: M.IN, 3: M.IN}}},
    3: {M.IN: 'B',
        M.OUT: 'D',
        M.LINK: 'ZZC',
        M.CONXNS: {M.IN: {0: M.IN, 1: M.OUT}, M.OUT: {4: M.IN}}},
    4: {M.IN: 'D',
        M.OUT: 'E',
        M.LINK: 'ZZD',
        M.CONXNS: {M.IN: {3: M.OUT}, M.OUT: {}}},
    M.CONFIG: {M.TEST_CHAR: 'B',
               M.LINK: 'QQQ',
               M.IN: 'B',
               M.OUT: 'B',
               M.CONXNS: {M.IN: {0: M.IN, 1: M.OUT, 3: M.IN},
                          M.OUT: {0: M.IN, 1: M.OUT, 3: M.IN}}}
}

BASIC_4CH = {
    0: {M.CONXNS: {M.IN: {2: M.IN, 5: M.OUT}, M.OUT: {1: M.IN}},
        M.IN: 'B',
        M.LINK: 'ZZZ',
        M.OUT: 'C'},
    1: {M.IN: 'C',
        M.OUT: 'A',
        M.LINK: 'ZZA',
        M.CONXNS: {M.IN: {0: M.OUT}, M.OUT: {}}},
    2: {M.CONXNS: {M.IN: {0: M.IN, 5: M.OUT}, M.OUT: {3: M.IN}},
        M.IN: 'B',
        M.LINK: 'ZZB',
        M.OUT: 'D'},
    3: {M.CONXNS: {M.IN: {2: M.OUT}, M.OUT: {4: M.IN}},
        M.IN: 'D',
        M.LINK: 'ZZC',
        M.OUT: 'E'},
    4: {M.CONXNS: {M.IN: {3: M.OUT}, M.OUT: {5: M.IN}},
        M.IN: 'E',
        M.LINK: 'ZZD',
        M.OUT: 'F'},
    5: {M.CONXNS: {M.IN: {4: M.OUT}, M.OUT: {0: M.IN, 2: M.IN}},
        M.IN: 'F',
        M.LINK: 'ZZE',
        M.OUT: 'B'},
    M.CONFIG: {M.CONXNS: {M.IN: {0: M.IN, 2: M.IN, 5: M.OUT},
                          M.OUT: {0: M.IN, 2: M.IN, 5: M.OUT}},
               M.IN: 'B',
               M.LINK: 'QQQ',
               M.OUT: 'B',
               M.TEST_CHAR: 'B'}}

WELCHMAN_1L = {
    0: {M.CONXNS: {M.IN: {2: M.OUT, 13: M.IN}, M.OUT: {}},
        M.IN: 'T',
        M.LINK: 'ZZZ',
        M.OUT: 'C'},
    2: {M.CONXNS: {M.IN: {12: M.OUT}, M.OUT: {0: M.IN, 13: M.IN}},
        M.IN: 'N',
        M.LINK: 'ZZB',
        M.OUT: 'T'},
    4: {M.CONXNS: {M.IN: {7: M.IN, 10: M.IN, 11: M.IN},
                   M.OUT: {5: M.IN, 9: M.OUT}},
        M.IN: 'E',
        M.LINK: 'ZZD',
        M.OUT: 'P'},
    5: {M.CONXNS: {M.IN: {4: M.OUT, 9: M.OUT}, M.OUT: {}},
        M.IN: 'P',
        M.LINK: 'ZZE',
        M.OUT: 'V'},
    7: {M.CONXNS: {M.IN: {4: M.IN, 10: M.IN, 11: M.IN},
                   M.OUT: {9: M.IN, 12: M.IN}},
        M.IN: 'E',
        M.LINK: 'ZZG',
        M.OUT: 'I'},
    9: {M.CONXNS: {M.IN: {7: M.OUT, 12: M.IN}, M.OUT: {4: M.OUT, 5: M.IN}},
        M.IN: 'I',
        M.LINK: 'ZZI',
        M.OUT: 'P'},
    10: {M.CONXNS: {M.IN: {4: M.IN, 7: M.IN, 11: M.IN}, M.OUT: {}},
         M.IN: 'E',
         M.LINK: 'ZZJ',
         M.OUT: 'D'},
    11: {M.CONXNS: {M.IN: {4: M.IN, 7: M.IN, 10: M.IN}, M.OUT: {}},
         M.IN: 'E',
         M.LINK: 'ZZK',
         M.OUT: 'U'},
    12: {M.CONXNS: {M.IN: {7: M.OUT, 9: M.IN}, M.OUT: {2: M.IN}},
         M.IN: 'I',
         M.LINK: 'ZZL',
         M.OUT: 'N'},
    13: {M.CONXNS: {M.IN: {0: M.IN, 2: M.OUT}, M.OUT: {}},
         M.IN: 'T',
         M.LINK: 'ZZM',
         M.OUT: 'K'},
    M.CONFIG: {M.CONXNS: {M.IN: {4: M.IN, 7: M.IN, 10: M.IN, 11: M.IN},
                          M.OUT: {4: M.IN, 7: M.IN, 10: M.IN, 11: M.IN}},
               M.IN: 'E',
               M.LINK: 'QQQ',
               M.OUT: 'E',
               M.TEST_CHAR: 'E'}}


class BOMBE_TEST_EASY1:
    left_rotor = 'I'
    middle_rotor = 'II'
    right_rotor = 'III'
    reflector = 'B'
    current_window_3 = 'YRP'
    ring_settings_3 = 'AAA'
    crib = "CBAA"
    cypher = "BACB"
    menu = {
        0: {'conxns': {'in': {2: 'out'}, 'out': {1: 'in', 3: 'out'}},
            'in': 'C',
            'menu_link': 'ZZZ',
            'out': 'B'},
        1: {'conxns': {'in': {0: 'out', 3: 'out'}, 'out': {2: 'in', 3: 'in'}},
            'in': 'B',
            'menu_link': 'ZZA',
            'out': 'A'},
        2: {'conxns': {'in': {1: 'out', 3: 'in'}, 'out': {0: 'in'}},
            'in': 'A',
            'menu_link': 'ZZB',
            'out': 'C'},
        3: {'conxns': {'in': {1: 'out', 2: 'in'}, 'out': {0: 'out', 1: 'in'}},
            'in': 'A',
            'menu_link': 'ZZC',
            'out': 'B'},
        'config': {'conxns': {'in': {1: 'out', 2: 'in', 3: 'in'},
                              'out': {1: 'out', 2: 'in', 3: 'in'}},
                   'in': 'A',
                   'menu_link': 'QQQ',
                   'out': 'A',
                   'test_char': 'A'}
    }


class BOMBE_TEST2:
    left_rotor = 'I'
    middle_rotor = 'II'
    right_rotor = 'III'
    reflector = 'B'
    current_window_3 = 'ABB'
    ring_settings_3 = 'ZZZ'
    crib = "EARTHVENUSMARSSATURN"
    cypher = "URDZTATXBQWXOBEFDENL"
    menu = {0: {'conxns': {'in': {6: 'in', 14: 'out', 17: 'out'},
                'out': {8: 'in', 17: 'in'}},
                'in': 'E',
                'menu_link': 'ZZZ',
                'out': 'U'},
            1: {'conxns': {'in': {11: 'in'}, 'out': {2: 'in', 18: 'in'}},
                'in': 'A',
                'menu_link': 'ZZA',
                'out': 'R'},
            2: {'conxns': {'in': {1: 'out', 18: 'in'}, 'out': {16: 'out'}},
            'in': 'R',
                'menu_link': 'ZZB',
                'out': 'D'},
            6: {'conxns': {'in': {0: 'in', 14: 'out', 17: 'out'}, 'out': {16: 'in'}},
            'in': 'E',
                'menu_link': 'ZZF',
                'out': 'T'},
            7: {'conxns': {'in': {18: 'out'}, 'out': {11: 'out'}},
            'in': 'N',
                'menu_link': 'ZZG',
                'out': 'X'},
            8: {'conxns': {'in': {0: 'out', 17: 'in'}, 'out': {13: 'out'}},
            'in': 'U',
                'menu_link': 'ZZH',
                'out': 'B'},
            11: {'conxns': {'in': {1: 'in'}, 'out': {7: 'out'}},
                 'in': 'A',
                 'menu_link': 'ZZK',
                 'out': 'X'},
            13: {'conxns': {'in': {14: 'in'}, 'out': {8: 'out'}},
                 'in': 'S',
                 'menu_link': 'ZZM',
                 'out': 'B'},
            14: {'conxns': {'in': {13: 'in'}, 'out': {0: 'in', 6: 'in', 17: 'out'}},
                 'in': 'S',
                 'menu_link': 'ZZN',
                 'out': 'E'},
            16: {'conxns': {'in': {6: 'out'}, 'out': {2: 'out'}},
                 'in': 'T',
                 'menu_link': 'ZZP',
                 'out': 'D'},
            17: {'conxns': {'in': {0: 'out', 8: 'in'},
                            'out': {0: 'in', 6: 'in', 14: 'out'}},
                 'in': 'U',
                 'menu_link': 'ZZQ',
                 'out': 'E'},
            18: {'conxns': {'in': {1: 'out', 2: 'in'}, 'out': {7: 'in'}},
                 'in': 'R',
                 'menu_link': 'ZZR',
                 'out': 'N'},
            'config': {'conxns': {'in': {1: 'in', 11: 'in'}, 'out': {1: 'in', 11: 'in'}},
                       'in': 'A',
                       'menu_link': 'QQQ',
                       'out': 'A',
                       'test_char': 'A'}}
