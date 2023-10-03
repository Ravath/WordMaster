# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 12:05:24 2023

@author: Ehlion
"""

from PIL import ImageTk,Image
from DataImage import DataImage

class ImageStore :

    def stretch_image(im : Image, image_dim : (int,int)) -> (int,int,int,int, float) :
        """"return (padx, pady, newx, newy, redimension_ratio)"""
        
        redimension_ratio = 1.0
        newx = im.width
        newy = im.height
        padx = 0
        pady = 0
        if im.width > image_dim[0] or im.height > image_dim[1] :
            newx = image_dim[0]
            newy = image_dim[1]
            if im.width > im.height :
                redimension_ratio = image_dim[0] / im.width
                newy = int(im.height * redimension_ratio)
            else :
                redimension_ratio = image_dim[1] / im.height
                newx = int(im.width * redimension_ratio)
        pady = (image_dim[0] - newy)/2
        padx = (image_dim[1] - newx)/2
        
        return (padx, pady, newx, newy, redimension_ratio)

    def __init__(self) :
        self.images = dict()
        
    def ask(self, imagepath:str, dim) -> (Image, tuple) :
        if not imagepath in self.images :
            self.images[imagepath] = dict()
        if not dim in self.images[imagepath] :
            self.images[imagepath][dim] = self.__open(imagepath, dim)
        return self.images[imagepath][dim]
    
    def __open(self, path, dim) :
        im = Image.open(path)
        position = ImageStore.stretch_image(im, dim)
        if position[4] != 1.0 :
            im = im.resize(position[2:4], Image.Resampling.LANCZOS)
        return (ImageTk.PhotoImage(im), position)
    
    def reset(self) :
        self.images.clear()