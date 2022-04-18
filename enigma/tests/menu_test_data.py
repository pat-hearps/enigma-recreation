
from enigma.constants import MENU as M

BASIC_4CH = {
    0: {M.CONXNS: {M.IN: {2: M.IN, 5: M.OUT}, M.OUT: {}},
        M.IN: 'B',
        M.LINK: 'ZZZ',
        M.OUT: 'C'},
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
