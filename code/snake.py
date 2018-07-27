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

class Snake(Env):


    def __init__(self, m, n, snake_len):
        self.m = m
        self.n = n
        self.features = {}

        self._symbol_map = {
            -4: utils.colorize(u'\u235F', 'red'), # dead head
            -3: utils.colorize(u'\u066D', 'cyan'), # food
            -2: utils.colorize(u'\u00B7', 'gray'), # blank
            -1: utils.colorize(u'\u235F', 'green'), # snake head
            (0, 3): utils.colorize(u"\u250c", "green"),
            (1, 2): utils.colorize(u"\u250c", "green"),
            (0, 1): utils.colorize(u"\u2510", "green"),    
            (3, 2): utils.colorize(u"\u2510", "green"),
            (2, 3): utils.colorize(u"\u2514", "green"),
            (1, 0): utils.colorize(u"\u2514", "green"),   
            (2, 1): utils.colorize(u"\u2518", "green"),
            (3, 0): utils.colorize(u"\u2518", "green"),
            (1, 1): utils.colorize(u"\u2500", "green"),
            (3, 3): utils.colorize(u"\u2500", "green"),
            (0, 0): utils.colorize(u"\u2502", "green"),        
            (2, 2): utils.colorize(u"\u2502", "green"),
        }

        self._key2action = {"w": 0, "a":1, "s":2, "d":3}
        


        #----------------
        # initialize self.info
        self.info = {
            "score": 0,
            "snake_len": snake_len,
            "snake_seq": [],
            "action_seq": [],
            "symbol_seq": [],
            "food": None,
        }

        i, j = m//2, n//2+snake_len//2
        for k in range(snake_len):
            self.info["snake_seq"].append((i,j-k))
            self.info["action_seq"].append(1)
            self.info["symbol_seq"].append(self._symbol_map[(1,1)])


        #-----------------
        # initialize board and observation
        self.observation = np.full((m, n), -2, dtype=np.int64)
        self._board = np.full((m, n), self._symbol_map[-2], dtype="<U16")


        # add snake body
        for (i,j), a in zip(self.info['snake_seq'], self.info['action_seq']):
            self.observation[i,j] = a
            self._board[i,j] = self._symbol_map[(1, 1)]

        # add snake head
        i,j = self.info['snake_seq'][-1]
        self.observation[i,j] = -1
        self._board[i,j] = self._symbol_map[-1]

        # add food
        i,j = self._get_random_food()
        self.observation[i,j] = -3
        self._board[i,j] = self._symbol_map[-3]
        self.info['food'] = (i, j)


    
    def get_input(self):
        
        x = getch()
        os.system("clear") 
        
        if x=="q":
            self.render()
            sys.exit("Thanks for playing!")
        elif x in ("w","a","s","d"):
            return self._key2action[x]
        else:
            self.render()
            return self.get_input()

    def _get_random_food(self):
        open_locs = list(zip(*np.where(self.observation==-2)))
        ind = np.random.randint(len(open_locs), size=1)[0]
        return open_locs[ind]


    def render(self):
        outfile = sys.stdout
        outfile.write(f"Score: {self.info['score']}\n")
        outfile.write(u"\u250c" + u"\u2500"*self.n + u"\u2510\n")
        for row in self._board.tolist():
            outfile.write(u"\u2502" + ''.join(row) + u"\u2502\n")
        outfile.write(u"\u2514" + u"\u2500"*self.n + u"\u2518\n")


    def step(self, action):
        
        # get head of snake
        head = self.info['snake_seq'][-1]
        i, j = head
        
        # implement action
        if action==0:   i-=1 # up
        elif action==1: j-=1 # left
        elif action==2: i+=1 # down
        elif action==3: j+=1 # right
        
        # check out of bounds or collision
        if i<0 or j<0 or i==m or j==n or (i,j) in self.info['snake_seq']:
            self._board[i, j] = self._symbol_map[-4]
            self.render()
            sys.exit('You lose!')
        
        # update food
        done = False
        if (i,j) == self.info['food']:

            # check if done
            if np.all(self.observation!=-2):
                done = True
                reward = 10
            else:
                food = self._get_random_food()
                self.info['food'] = food
                self.info['score'] +=1
                self.info['snake_len'] +=1
                reward = 1

                # update food
                self.observation[food[0], food[1]] = -3
                self._board[food[0], food[1]] = self._symbol_map[-3]

        else:
            # update tail
            tail = self.info['snake_seq'].pop(0)
            self.observation[tail[0], tail[1]] = -2
            self._board[tail[0], tail[1]] = self._symbol_map[-2]
            self.info['symbol_seq'].pop(0)
            self.info['action_seq'].pop(0)
            reward = 0

        # update observation
        last_action = self.info['action_seq'][-1]    
        self.observation[head[0], head[1]] = last_action
        self.observation[i, j] = -1
        
        # update board
        self._board[head[0], head[1]] = self._symbol_map[(last_action, action)]
        self._board[i, j] = self._symbol_map[-1]

        # update info            
        symbol = self._symbol_map[(last_action, action)]
        self.info['symbol_seq'].append(symbol)
        self.info['action_seq'].append(action)
        self.info['snake_seq'].append((i,j))
            

        return self.observation, done, reward, self.info


if __name__ == "__main__":

    def get_args():
        parser = argparse.ArgumentParser()
        parser.add_argument("-m", "--n_rows", default=4, type=int, help="number of rows")
        parser.add_argument("-n", "--n_cols", default=8, type=int, help="number of rows")
        parser.add_argument("-l", "--snake_len", default=3, type=int, help="initial length of snake")
        return parser.parse_args()

    args = get_args()
    m = args.n_rows
    n = args.n_cols
    snake_len = args.snake_len


    env = Snake(m, n, snake_len)
    os.system("clear") 

    while True:
        env.render()
        a = env.get_input()
        _, done, _, _ = env.step(a)
        if done:
            env.render()
            sys.exit('You win!')
