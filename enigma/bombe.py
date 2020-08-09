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

class Bombe:
    
    def __init__(self,menu,left_rotor='I',middle_rotor='II',right_rotor='III',reflector='B'):
        """Needs to be initialised with a menu, which is a dictionary with a specific format of instructions
        for how scramblers are to be interconnected, and their starting positions"""
        self.left_rotor = left_rotor
        self.middle_rotor = middle_rotor
        self.right_rotor = right_rotor
        self.reflector = reflector
        self.scramblers = {}
        self.register = {'status':{char:0 for char in entry}}
        self.current_sum = sum(self.register['status'].values())
        self.run_record = {}

        self.menu = menu
        """Scrambler setup, creating a scrambler corresponding to each menu item"""
        for scr_id,descriptor_dict in self.menu.items():
            if scr_id == 'config':
                self.test_char = self.menu['config']['test_char']
                self.register['conxns'] = self.menu['config']['conxns']['in']
            else:
                self.scramblers[scr_id] = Scrambler(self.left_rotor,self.middle_rotor,self.right_rotor,self.reflector,
                                                      menu_link=descriptor_dict['menu_link'],conx_in=descriptor_dict['conxns']['in'], conx_out=descriptor_dict['conxns']['out'])
        self.lowest_scrambler_order = min([key for key in self.scramblers.keys()])
        self.identity_scrambler = self.scramblers[self.lowest_scrambler_order]
        
        """Diagonal Board setup, could possible integrate into Scrambler setup loop above"""
        self.diagonal_board_wiring = {}
        for scr_id,descriptor_dict in self.menu.items():
            if scr_id == 'config':
                pass
            else:
                for inorout in ['in','out']:
                    thisletter = descriptor_dict[inorout]
                    if thisletter not in self.diagonal_board_wiring.keys():
                        self.diagonal_board_wiring[thisletter] = {scr_id:inorout}
                    else:
                        self.diagonal_board_wiring[thisletter][scr_id] = inorout
        ### identity scrambler is just the first one in the sequence of letters used from the crib.
        ### will probably be 0/ZZZ unless that particular letter pair from the crib/cypher has not been
        ### used in the menu
    
    def pulse_connections(self):
        """Goes through every scrambler (once only), and updates in and out terminals with live feeds via conx_in and
        conx_out from its connected scramblers. Should be run iteratively to exhaustion."""
        for scr1id,scrambler in self.scramblers.items():
            ## i.e for each scrambler in the enigma, we're going to loop through it's conxns['in'] and conxns['out'] 
            ## dictionaries and check its connected scramblers to match any live wires
            for ior in ['in','out']:
                for scr2id,side in scrambler.conxns[ior].items():
                    ## for this scrambler, go through the conxns 'in' or 'out' dict. It has the other scrambler you need to 
                    ## look at (scr2id, or the number/position label) and whether you're looking at the 'in' or 'out' side
                    for ch,io in self.scramblers[scr2id].status[side].items():
                        # look through the scrambler's status for that side (in or out)
                        if io == 1:   # and if it has a live wire
                            scrambler.status[ior][ch] = 1 # set the corresponding character in the conxns dict of the 
                
    def sync_diagonal_board(self):
        """Current theory is ???"""
        for scr1id, scrambler in self.scramblers.items():
            for inorout in ['in','out']:
                connection_character = self.menu[scr1id][inorout] ## ie the single letter 'A', 'M' etc that is the menu connection
                for character in self.diagonal_board_wiring.keys():
                    if scrambler.status[inorout][character] == 1:
                        for scr2id, side in self.diagonal_board_wiring[character].items():
                            self.scramblers[scr2id].status[side][connection_character] = 1
                        
                
    def sync_test_register(self):
        """similar to pulse_connections in that it updates terminals of scramblers, but is solely about the
        interconnections between the test register and those scramblers which are connected to it"""
        for scr2id,side in self.register['conxns'].items():  ## side = 'in' or 'out'
            ## for each of the scrambler terminals connected to the test register
            for ch,io in self.scramblers[scr2id].status[side].items():
                ## first sync any live wires from the scrambler to the test register
                if io == 1:   
                    self.register['status'][ch] = 1
            for ch,io in self.register['status'].items():
                ## but then also sync any live wires from the test register to the scrambler
                if io == 1:
                    self.scramblers[scr2id].status[side][ch] = 1           

    
    def light_character(self,in_character):
        """just need a way to put in the initial character input into all of the scramblers"""
        self.register['status'][self.test_char] = 1
    
    def update_all(self):
        """For every scrambler, runs update() which passes live terminals through the scrambler - from in to out
        and vice versa, for whatever the current position is"""
        for scrambler in self.scramblers.values():
            scrambler.update()
            
    def spin_scramblers(self):
        """Runs step_enigma for all scramblers, spinning the right rotor once and perhaps the middle and left if
        they are in their notch positions"""
        for scrambler in self.scramblers.values():
            scrambler.step_enigma()
            
    def reset_scramblers_and_register(self):
        """ resets all scrambler statuses and test register to 0 for all alphabet characters"""
        for scrambler in self.scramblers.values():
            scrambler.reset_status()
        self.register['status'] = {char:0 for char in entry}
    
    def check_this_lineup(self):
        """For running to exhaustion on a particular bombe scrambler lineup. 
        Loops through pulsing connections between scramblers and syncing back to the test register
        until the sum of live connections at the test register remains unchanged for two successive loops."""
        self.reset_scramblers_and_register()   # first make sure all scrambler inputs/outputs (statuses) are reset to zero
        self.light_character(self.test_char)   # light up the one test character
        self.sync_test_register()              # do the first syncing of test register, sending the signal out to the 
                                                # scramblers which are connected to the test register
            
    ### initialise the three sum variables (current_sum, previous_sum and olderer_sum) to keep track of whether 
    ### the sum of live connections have remained unchanged
        self.current_sum = sum(self.register['status'].values())
        self.track_sums = [0,1]
        self.lineup_iters = 0   # this is just to keep track of how many iterations it took to reach a steady status
        while len(set(self.track_sums[-5:])) != 1: # i.e. keep going until the register status is unchanged for 5 iterations
            self.update_all()                      # the 5 is somewhat arbitrary. Testing on one menu found no more than 3 continuous
            self.pulse_connections()               # occurrences of an incomplete status but could be different for other menus. 
#             self.sync_diagonal_board()
            self.sync_test_register()
            self.current_sum = sum(self.register['status'].values())
            self.track_sums.append(self.current_sum)
            self.lineup_iters += 1
    
    def step_and_test(self):
        """the main function to use for looping through all possible combinations of rotor positions, 
        testing the connections at each step using check_this_lineup()"""
        self.spin_scramblers()
        self.check_this_lineup()
        self.run_record[self.identity_scrambler.current_position] = (self.current_sum,self.lineup_iters,self.track_sums)
        if self.current_sum != 26:
            print('drop:  ',self.identity_scrambler.current_position, 'livestatus:', self.current_sum)
            

    def pdf_scrambler_statuses(self):
        """pdf = pandas dataframe
        Refreshes self.flash_scrambler_statuses variable to be a pandas dataframe summarising
        the current status (in==on/out==on) for each 26 alphabet letters for each of the scramblers in the Bombe"""
        bigdict = {}
        bigdict['REG'] = {k:('X' if v==1 else '') for k,v in self.register['status'].items()}
        for scr_id,scrambler in self.scramblers.items():
            littledict = {k:{l:(k[0].upper() if r == 1 else '') for l,r in v.items()} for k,v in scrambler.status.items()}
            bigdict[scr_id] ={k1:v1+littledict['out'][k1] for k1,v1 in littledict['in'].items()}
        self.flash_scrambler_statuses = pd.DataFrame(bigdict).T
        
    def nx_setup(self,scale=1,figsize=(15,10),width_of_scrambler=0.1,height_of_scrambler=0.06):
        """For creating NetworkX graphs. Setting up base graph (BG), detailed graph (TG), figure and axes for displaying scrambler connections
        Will also effectively reset the nx Graphs"""
        self.BG = nx.Graph()
        scramblers_in_menu = [k  if type(k) == int else 'REG' for k in menu.keys()]
        self.BG.add_nodes_from(scramblers_in_menu)
        
        base_edges = set()
        for scr_id,descriptor_dict in self.menu.items():
            if scr_id == 'config':
                scr_id = 'REG'
            for inorout in ['in','out']:
                for connected_scrambler,ior in descriptor_dict['conxns'][inorout].items():  
                    ## the dictionary of connections that is the value for each 'conx_in/out' keys
                    base_edges.add(frozenset([scr_id,connected_scrambler])) # set of sets so not to double up

        base_edges = [tuple(be) for be in base_edges]  # turn set of frozensets into list of tuples
        self.BG.add_edges_from(base_edges)
#         self.base_pos_for_nx = nx.circular_layout(self.BG,scale=scale)
        self.base_pos_for_nx = nx.spring_layout(self.BG,scale=scale)
        self.base_pos_for_nx['REG'] = np.array([0,-0.9])
        
        ## This section for the detailed graph (TG) 
        self.TG = nx.Graph()
        ## this for-loop adds all nodes to the graph
        for scr_id in scramblers_in_menu:           ## for each scrambler in the menu
            for ch in entry:         ## for each letter A-Z
                for i in ['I','O']:  ## for each end (in/out) of the double-ended scrambler
                    if scr_id == 'REG': ## i = X (not I or O) if it's the register
                        i = 'X'
                    this_node_label = f"{scr_id}-{i}-{ch}"
                    self.TG.add_node(this_node_label)  ## add a node to the graph
                    self.TG.nodes[this_node_label]["color"] = grey
        
        ## this for-loop adds edges for scrambler connections to the graph
        self.inter_scr_edges = set()
        for scr_id,descriptor_dict in self.menu.items():                       # for each scrambler (scr_id) and its spec dict
            for inorout in ['in','out']:                          # go thru the conx_in and conx_out dicts
                if scr_id == 'config':   # this just for dealing with the register
                    first_node = 'REG-X-'
                else:
                    first_node = f"{scr_id}-{iomap[inorout]}-"           # label the start of the 1st node, with either I/O
                for connected_scrambler,ior in descriptor_dict['conxns'][inorout].items():          # go thru the in/out connections
                    second_node = f"{connected_scrambler}-{iomap[ior]}-"        # label the start of the 2nd node
                    for ch in entry:                                                    # for each letter A-Z
                        self.inter_scr_edges.add(frozenset([first_node+ch,second_node+ch])) # create 26 nodes with each of 1st/2nd node plus letter
        
        ## bit of data reformatting for the edges
        self.inter_scr_edges = [list(fs) for fs in self.inter_scr_edges]
        for edge in self.inter_scr_edges:
            edge.append({'color': grey})
        self.inter_scr_edges = [tuple(fs) for fs in self.inter_scr_edges]
        self.TG.add_edges_from(self.inter_scr_edges)
        
        wrange_of_letters = list(np.linspace(-0.5*width_of_scrambler,0.5*width_of_scrambler,26))

        self.manual_pos = {}

        for node in self.TG.nodes():
            scr_id,io,ch = node.split('-')
            try:
                scr_id = int(scr_id)
            except:
                pass
            x,y = self.base_pos_for_nx[scr_id]

            if io == 'I':                       ## spacing apart the in from the out nodes
                y += -0.5 * height_of_scrambler ## 'in' (I) is below
            else:
                y += 0.5 * height_of_scrambler  ## 'out' (O) is above

            x += wrange_of_letters[entry.index(ch)]
            self.manual_pos[node] = np.array([x,y])
            
        self.colors = [self.TG[u][v]['color'] for u,v in self.TG.edges()]
        
        fig, ax = plt.subplots(figsize=figsize)
        nx.draw_networkx_nodes(self.BG,pos=self.base_pos_for_nx)
        nx.draw_networkx_labels(self.BG,pos=self.base_pos_for_nx)
        nx.draw_networkx_edges(self.TG,pos=self.manual_pos,edge_color=self.colors)
        
    def graph_nx(self,figsize=(15,10),node_size=3):
        """First updates nx_graph edge colors based on current scrambler statuses,
        then redraws nx_graph visualisation"""
        for u,v in self.TG.edges():   ## reset previously red to orange
            if self.TG[u][v]['color'] == red:
                self.TG[u][v]['color'] = orange
        for u,v in self.TG.nodes.items():
            if self.TG.nodes[u]['color'] == red:
                self.TG.nodes[u]['color'] = orange
                
        for scr_id, scrambler in self.scramblers.items():
            for ior in ['in','out']:
                for ch, onoff in scrambler.status[ior].items():
                    if onoff == 1:
                        first_live_node = f"{scr_id}-{iomap[ior]}-{ch}"
                        if self.TG.nodes[first_live_node]['color'] == grey:
                            self.TG.nodes[first_live_node]['color'] = red
                        cypher_node = f"{scr_id}-{invsoutmap[ior]}-{scrambler.full_scramble(ch)}"
                        ## if statement below will add the intra_scrambler edges (letter in --> cypher out)
                        ## stepwise as each node gets lit up
                        if (first_live_node,cypher_node) not in self.TG.edges():
                            self.TG.add_edge(first_live_node, cypher_node, color=red)
                        
                        for bid, inout in scrambler.conxns[ior].items():
                            second_live_node = f"{bid}-{iomap[inout]}-{ch}"
                            try:
                                if self.TG.edges[(first_live_node, second_live_node)]['color'] == grey:
                                    self.TG.edges[(first_live_node, second_live_node)]['color'] = red
                            except:
                                if self.TG.edges[(second_live_node, first_live_node)]['color'] == grey:
                                    self.TG.edges[(second_live_node, first_live_node)]['color'] = red

        for ch, onoff in self.register['status'].items():
            if onoff == 1:
                first_live_node = f"REG-X-{ch}"
                for bid,inout in self.register['conxns'].items():
                    second_live_node = f"{bid}-{iomap[inout]}-{ch}"
                    try:
                        if self.TG.edges[(first_live_node, second_live_node)]['color'] == grey:
                            self.TG.edges[(first_live_node, second_live_node)]['color'] = red
                    except:
                        if self.TG.edges[(second_live_node, first_live_node)]['color'] == grey:
                            self.TG.edges[(second_live_node, first_live_node)]['color'] = red
                        
        self.edge_colours = [self.TG[u][v]['color'] for u,v in self.TG.edges()]
        self.node_colours = [v['color'] for u,v in self.TG.nodes.items()]
        fig, ax = plt.subplots(figsize=figsize)
        nx.draw_networkx_nodes(self.BG,pos=self.base_pos_for_nx)
        nx.draw_networkx_labels(self.BG,pos=self.base_pos_for_nx)
        nx.draw_networkx_edges(self.TG,pos=self.manual_pos,edge_color=self.edge_colours)
        if node_size > 0:
            nx.draw_networkx_nodes(self.TG,pos=self.manual_pos,node_size=node_size,node_color=self.node_colours)