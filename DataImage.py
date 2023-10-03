# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 11:01:34 2023

@author: Ehlion
"""

import os
from DataCaption import DataCaption

class DataImage :
    
    def __init__(self) :
        self.filepath = ""
        # only if is the crop version of an original image
        self.original_image = None # as DataImage filepath
        self.zones = []
        
        # DataCaption
        self.__current_caption = DataCaption()
        self.__original_caption = DataCaption()
    
    # properties
    @property
    def current_caption(self):
        return self.__current_caption
    @current_caption.setter
    def current_caption(self, value):
        self.__current_caption.words = value
    @property
    def original_caption(self):
        return self.__original_caption
    @original_caption.setter
    def original_caption(self, value):
        self.__original_caption.words = value
    
    # JSON
    def load_json(self, dp) :
        self.filepath = dp["picture"]
        self.original_caption.csv_init(dp["original_caption"])
        self.current_caption.csv_init(dp["current_caption"])
        self.original_image = dp.get("original_image")
        for jzone in dp["zones"] :
            newZone = ImageZone()
            newZone.load_json(jzone)
            self.zones.append(newZone)
    def save_json(self) :
        save_zones = []
        for z in self.zones :
            save_zones.append(z.save_json())
        return {"picture" : self.filepath,
                "original_caption" : self.original_caption.to_csv(),
                "current_caption" : self.current_caption.to_csv(),
                "zones" : save_zones,
                "original_image" : self.original_image}
    
    # misc
    def is_original(self) :
        return self.original_filepath == None
    
    def set_picture(self, picture_path : str) :
        self.filepath = picture_path

    def set_caption(self, caption_path : str) :
        f = open(caption_path, "r")
        self.current_caption.csv_init(f.read())
    
    def init_original_caption(self) :
        self.original_caption.words = self.current_caption.words.copy()
    
    def get_file_name(self) :
        return os.path.basename(self.filepath)
    def get_caption_filepath(self) :
        return self.filepath.replace(".png", ".txt")
    
    def contains(self, w:str) :
        if w in self.current_caption.words :
            return True
        for z in self.zones :
            if w in z.caption.words :
                return True
        return False
    
    def remove_tag(self, w : str) :
        if w in self.current_caption :
            self.current_caption.remove(w)
        for z in self.zones :
            if w in z.caption :
                z.caption.remove(w)
        


class ImageZone :
    
    def __init__(self, name : str = "Zone", dim = None) :
        # (int,int) => dot
        # (int,int, int,int) => Rect
        self.dim = dim
        self.name = name
        self.__caption = DataCaption()
        self.cropped_image = None # as DataImage filepath
        
    @property
    def caption(self):
        return self.__caption
    @caption.setter
    def caption(self, value):
        self.__caption.words = value
    
    # JSON
    def load_json(self, dp) :
        self.name = dp["name"]
        self.dim = dp["dim"]
        self.caption.csv_init(dp["caption"])
        self.cropped_image = dp.get("cropped_image")
    def save_json(self) :
        return {"name" : self.name,
                "dim" : self.dim,
                "caption" : self.caption.to_csv(),
                "cropped_image" : self.cropped_image}


