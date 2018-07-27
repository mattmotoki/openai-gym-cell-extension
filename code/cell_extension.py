#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import numpy as np
from gym import Env, utils
from gym.spaces import Box, Discrete

def getch():
    """ 
    Get single character input
    https://stackoverflow.com/questions/510357/python-read-a-single-character-from-the-user
    """
    import tty, sys, termios

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

class CellExtension(Env):


    def __init__(self, m, n):
        self.m = m
        self.n = n
        self.features = {}
        self._symbol_map = {
            -1: u'\u0020', # blank        
            (0,0,0,0): u'\u00B7', # ·        
            (0,1,0,1): u'\u2500', # ─
            (1,0,1,0): u'\u2502', # │
            (1,0,1,1): u'\u251c', # ├
            (1,1,1,0): u'\u2524', # ┤
            (0,1,1,1): u'\u252c', # ┬
            (1,1,0,1): u'\u2534', # ┴
            (1,1,1,1): u'\u253c', # ┼
            (0,0,1,1): u'\u250c', # ┌  
            (0,1,1,0): u'\u2510', # ┐   
            (1,0,0,1): u'\u2514', # └
            (1,1,0,0): u'\u2518', # ┘
            (0,1,0,0): u'\u2574', # ╴
            (1,0,0,0): u'\u2575', # ╵
            (0,0,1,0): u'\u2576', # ╶
            (0,0,0,1): u'\u2577', # ╷
        }

        self._player_color = ['green', 'magenta']
        
        self._key2action = {"\r":-1, "w": 0, "a":1, "s":2, "d":3}

        #-----------------
        # initialize board and observation
        self.observation = np.full((m, n), -1, dtype=np.int64)
        self._board = np.full((m, n), self._symbol_map[-1], dtype="<U16")
        
        #----------------
        # initialize self.info
        self.info = {
            "score": 0,
            "player0_seq": [],
            "player1_seq": [],
        }

    def get_symbol(self, state, player):
        symbol = self._symbol_map[state]
        color = self._player_color[player] if player else None
        return utils.colorize(symbol, color, highlight=color)    
    
    def get_input(self):
        
        x = getch()
        os.system("clear") 
        if x=="q":
            self.render()
            sys.exit("Thanks for playing!")
        elif x in ("\r","w","a","s","d"):
            return self._key2action[x]

        else:
            self.render()
            return self.get_input()

    def render(self):
        outfile = sys.stdout
        outfile.write(f"Score: {self.info['score']}\n")

if __name__ == "__main__":

    def get_args():
        parser = argparse.ArgumentParser()
        parser.add_argument("-m", "--n_rows", default=4, type=int, help="number of rows")
        parser.add_argument("-n", "--n_cols", default=8, type=int, help="number of rows")
        return parser.parse_args()

    args = get_args()
    m = args.n_rows
    n = args.n_cols

    env = CellExtension(m, n)
    os.system("clear") 

    while True:
        print(env.get_input())