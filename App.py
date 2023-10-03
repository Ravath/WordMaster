# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 11:00:27 2023

@author: Ehlion
"""

import os
import json
from DataImage import DataImage
from WordRelation import WordRelation, RelationType
from Vocabulary import Vocabulary
from PIL import ImageTk,Image, ImageOps

class App :
    
    save_filename = "save.json"
    flip_suffix = "_flip"
    
    def __init__(self) :
        self.data = [] #DataImage[]
        self.vocabulary = Vocabulary()
        self.currentdir = None
    
    def reset(self) :
        self.data.clear()
        self.vocabulary.reset()
    
    def add_data(self, data:DataImage) :
        self.data.append(data)
        self.vocabulary.add_words(data.current_caption)
    
    def read_folder(self, dirpath : str) :
        
        self.reset()
        self.currentdir = dirpath
        
        for f in os.listdir(dirpath) :
            fp = os.path.join(dirpath, f)
            fname, fextension = os.path.splitext(f)
            
            if fextension == ".txt" and not fname.endswith(App.flip_suffix) :
                picture_filename = fname + ".png"
                if not os.path.exists(os.path.join(dirpath, picture_filename)) :
                    print(f"Error : could not find data picture {picture_filename}")
                    pass
                
                d = DataImage()
                d.set_picture(os.path.join(dirpath, picture_filename))
                d.set_caption(fp)
                d.init_original_caption()
                self.add_data(d)
    
    def save_json(self, dirpath : str = None) :
        
        if dirpath == None :
            dirpath = self.currentdir
        
        save_data = []
        for d in self.data :
            save_data.append(d.save_json())
        
        f = open(os.path.join(dirpath, App.save_filename), "w")
        f.write(json.dumps(save_data, sort_keys=True, indent=4))
        f.close()

    def load_json(self, dirpath : str) :
        
        self.reset()
        self.currentdir = dirpath
        
        file = open(os.path.join(dirpath, App.save_filename), "r")
        data = json.loads(file.read())
        for dp in data :
            d = DataImage()
            d.load_json(dp)
            self.data.append(d)
    
    def load_archive(self, dirpath : str) :
        if os.path.exists(os.path.join(dirpath, App.save_filename)) :
            self.load_json(dirpath)
        else :
            self.read_folder(dirpath)
    
    def build_vocabulary(self) :
        self.vocabulary.reset()
        for d in self.data :
            self.vocabulary.add_words(d.current_caption)
    
    def replace(self, old_word:str, new_word:str) :
        
        count = 0
        if old_word in self.vocabulary.words :
            
            if new_word in self.vocabulary.words :
                count = self.vocabulary.words[new_word]
            else :
                self.vocabulary.words[new_word] = 0
                
            for d in self.data :
                if old_word in d.current_caption.words :
                    if not new_word in d.current_caption.words :
                        count += 1
                        index = d.current_caption.words.index(old_word)
                        d.current_caption.words[index] = new_word
                    else :
                        d.current_caption.words.remove(old_word)
            
            self.vocabulary.words[new_word] = count
            self.vocabulary.words[old_word] = 0
    
    def update_caption_files(self) :
        
        # TODO : implement word order management
        
        for d in self.data :
            # build caption
            words = d.current_caption.words
            for z in d.zones :
                words.extend(z.caption.words)
            words = list(dict.fromkeys(words))
            
            # write file
            caption_filepath = d.filepath.replace(".png", ".txt")
            captionfile = open(caption_filepath, "w")
            captionfile.write(",".join(words))
            captionfile.close()
    
    def scan_relations(self, rel : WordRelation) :
        
        for d in self.data :
            
            if rel.is_relevant(d.current_caption.words) :
                found = rel.scan_file(d.current_caption.words)
                print(f"{d.get_file_name()} : \n\t{found}")
    
    def next_image(self, data : DataImage) :
        index = self.data.index(data) + 1
        if index >= len(self.data) : index = 0
        return self.data[index]

    def prev_image(self, data : DataImage) :
        index = self.data.index(data) - 1
        if index < 0 : index = len(self.data)-1
        return self.data[index]
    
    def find_data_by_filepath(self, filepath:str) -> DataImage :
        for d in self.data :
            if d.filepath == filepath :
                return d
        
    def create_flips(self) :
        for d in self.data :
            fname, fextension = os.path.splitext(d.filepath)
            dimage = DataImage()
            flip_path = fname + App.flip_suffix + fextension

            # create new caption file
            f = open(fname + App.flip_suffix + ".txt", "w")
            f.write(d.current_caption.to_csv())
            f.close()
            # create new png file
            raw_image = Image.open(d.filepath)
            flip = ImageOps.mirror(raw_image)
            flip.save(flip_path, "PNG")
        
    def add_word(self, new_word:str) :# TODO manage case ?
        """Add a new_word at the start of captions. Change position to first position if already exists."""
        for d in self.data :
            if new_word in d.current_caption.words:
                index = d.current_caption.words.index(new_word)
                d.current_caption.pop(index)
                d.current_caption.insert(0, new_word)
            else :
                d.current_caption.insert(0, new_word)
                self.vocabulary.add_word(new_word)
            
    def remove_word(self, rw:str) :
        """remove a word from the captions."""
        for d in self.data :
            if rw in d.current_caption.words:
                index = d.current_caption.words.index(rw)
                d.current_caption.pop(index)
        self.vocabulary.remove_word(rw)
    
    def remove_picture(self, p : DataImage) :
        d = self.data.index(p)
        print(d)
        
        for pict in self.data :
            if pict.original_image == p.filepath :
                p.original_image = None
        os.remove(p.filepath)
        os.remove(p.get_caption_filepath())
        del self.data[d]
    
    def replace_spaces(self) :
        for d in self.data :
            problems = [w for w in d.current_caption.words if " " in w]
            
            for p in problems :
                self.replace(p, p.replace(" ", "_"))

if __name__ == "__main__" :
    test_data = r"K:\StableDiffusion\Train_Lora\Ferres\V20\Images\200_Data"
    test_data = r"K:\StableDiffusion\Train_Lora\Masafumi\Images\200_masaFrame"
    
    a = App()
    
    a.read_folder(test_data)
    # a.save_json(test_data)
    # a.load_json(test_data)
    
    rels = [
        # PARTITIONS
        WordRelation(RelationType.Partition, "Sexe", "", 
                     ["1girl", "1boy", "girl", "boy", "woman", "man"]),
        WordRelation(RelationType.Partition, "Hair length", "", 
                     ["long_hair", "short_hair", "very_long_hair"]),
        WordRelation(RelationType.Partition, "Hair color", "", 
                     ["grey_hair", "pink_hair", "white_hair", "blond_hair", "blonde_hair", "black_hair", "red_hair", "brown_hair", "blue_hair", "green_hair", "purple_hair", "orange_hair"]),
        WordRelation(RelationType.Partition, "Eye color", "", 
                     ["grey_eyes", "pink_eyes", "white_eyes", "yellow_eyes", "black_eyes", "red_eyes", "brown_eyes", "blue_eyes", "green_eyes", "purple_eyes", "orange_eyes", "closed_eyes"]),
        WordRelation(RelationType.Partition, "Breasts size", "", 
                     ["breasts", "chest", "flat_chest", "small_breasts", "medium_breasts", "huge_breasts"]),
        WordRelation(RelationType.Partition, "Scenery", "", 
                     ["outside", "inside"]),
        # DEFINITIONS
        WordRelation(RelationType.Definition, "Yoke", "yoke", 
                     ["metal_bar", "cuffs", "handcuff", "bdsm", "bondage"]),
        # QUALIDIANTS
        WordRelation(RelationType.Definition, "Masafumi frames", "Metal_Frame",
                     ["bdsm", "bondage", "restraints", "stationary_restraints", "metal", "cuff", "handcuff"]),
        WordRelation(RelationType.Qualifiant, "Masafumi frames", "Metal_Frame", 
                     ["fountain", "packed", "contorsion", "parrot", "dove", "clock", "wall", "table", "golfish", "stairs", "mermaid", "serving_table"]),
        WordRelation(RelationType.Qualifiant, "Gag type", "gag", 
                     ["ball_gag", "ring_gag", "bite_gag", "spider_gag", "horse_gag", "cleave_gag"]),
        WordRelation(RelationType.Qualifiant, "Text", "watermark",
                     ["artist_name", "web_address", "title", "date", "dated", "signature"]),
        # EXCLUSIVE
        WordRelation(RelationType.Exclusive, "Man Only", "girl",
                     ["bald", "facial_hair", "beard", "mustache"]),
        # CORRELATION
        WordRelation(RelationType.Correlation, "Nudity", "",
                     ["nude", "completly_nude", "navel", "breasts", "nipple", "nipples", "pussy", "ass", "barefoot", "sole", "soles"]),
        WordRelation(RelationType.Correlation, "Blurriness", "",
                     ["blur", "blurry_foreground", "blurry_background"]),
        WordRelation(RelationType.Correlation, "BDSM", "",
                     ["bdsm", "bondage", "shibari", "rope", "chain", "tied", "bound", "restrained", "stationary_restraints"]),
        WordRelation(RelationType.Correlation, "Bondage", "",
                     ["bondage", "bond", "tied",
                      "bound_arms", "bound_legs", "bound_wrists", "bound_ankles", "bound_arm", "bound_legs", "bound_wrists", "bound_ankles",
                      "bound_arm", "bound_leg", "bound_wrist", "bound_ankle", "bound_arm", "bound_leg", "bound_wrist", "bound_ankle",
                      "tied_arms", "tied_legs", "tied_wrists", "tied_ankles", "tied_arm", "tied_legs", "tied_wrists", "tied_ankles",
                      "tied_arm", "tied_leg", "tied_wrist", "tied_ankle", "tied_arm", "tied_leg", "tied_wrist", "tied_ankle"]),
        WordRelation(RelationType.Correlation, "Shibari", "",
                     ["shibari", "rope", "red_rope", "tied", "bound", "restrained", "arms_in_the_back", "arms_behind_back", "breast_bondage", "kinbaku", "hogtie", "box_tie", "tied_arms", "tied_legs", "suspension"]),
    ]
    
    for rel in rels :
        print(rel.name, " --> ", rel.words)
        a.scan_relations(rel)
        print()
    
    # a.replace("electric_shock", "electricity")
    
    s = sorted(a.vocabulary.words.items(), key=lambda x:x[1])
    for k,i in s :
        print(f"{k} : {i}")
    
    # a.update_caption_files()
    
    # TODO : remove doublons losque charge les mots