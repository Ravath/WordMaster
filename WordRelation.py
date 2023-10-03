# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 22:42:49 2023

@author: Ehlion
"""

from enum import Enum

class RelationType(Enum):
    Partition = 1
    Correlation = 2
    Qualifiant = 3
    Synonyme = 4
    Definition = 5
    Exclusive = 6


Color = Enum('Color', ['RED', 'GREEN', 'BLUE'])

class WordRelation :
    
    def __init__(self,
                 relation_type : RelationType = RelationType.Correlation,
                 relation_name : str  = "Relation Name",
                 class_name : str  = " Name",
                 class_words : list[str] = []) :
        self.name = relation_name
        self.RelationType = relation_type
        self.class_name = class_name
        self.words = class_words
    
    def is_relevant(self, caption : list[str]) :
        if self.RelationType == RelationType.Qualifiant or \
            self.RelationType == RelationType.Definition or \
            self.RelationType == RelationType.Exclusive :
            return self.class_name in caption
        return True
    
    def scan_file(self, caption : list[str]) :
        return [w for w in self.words if w in caption]

