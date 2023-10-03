# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 18:41:25 2023

@author: Ehlion
"""

from DataCaption import DataCaption

class Vocabulary :
    
    def __init__(self) :
        self.words = {}
    
    def reset(self) :
        self.words.clear()
    
    def add_word(self, w : str) :
        if w in self.words :
            self.words[w] += 1
        else :
            self.words[w] = 1
    
    def add_words(self, caption : DataCaption) :
        for w in caption.words :
            if w in self.words :
                self.words[w] += 1
            else :
                self.words[w] = 1
            
    def dec_word(self, w : str) :
        if w in self.words :
            self.words[w] -= 1
    
    def remove_word(self, w:str) :
        self.words[w] = 0