# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 11:01:45 2023

@author: Ehlion
"""
import re

class DataCaption :

    def clean_text(text : str) -> list[str] :
        words = [w.strip() for w in re.split(r",|\n",text) if len(w) > 0 and not w.isspace()]
        return list(dict.fromkeys(words))

    def __init__(self) :
        self.words = []
        

    # csv management
    def csv_init(self, data:str) :
        self.words = DataCaption.clean_text(data)
    def to_csv(self) :
        return ",".join(self.words)
    
    # reimplement list fonctionalities
    def __iter__(self) :
        """Implements spectific iteration access for the class."""
        return [w for w in self.words].__iter__()
    def __getitem__(self, key) :
        """Implements spectific '[]' access for the class."""
        return self.words[key]
    def __setitem__(self, index, item) :
        """Implements spectific '[]' access for the class."""
        self.words[index] = item

    def insert(self, index, item) :
        self.words.insert(index, item)

    def append(self, item) :
        self.words.append(item)

    def pop(self, item) :
        self.words.pop(item)

    def remove(self, item) :
        self.words.remove(item)

    def extend(self, other) :
        if isinstance(other, type(self)):
            self.words.extend(other)
        else:
            self.words.extend(item for item in other)
