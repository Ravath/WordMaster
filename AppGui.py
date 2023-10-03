# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 14:24:33 2023

@author: Ehlion
"""

import os
import re
from tkinter import *
from tkinter import filedialog
from PIL import ImageTk,Image
from functools import partial
from App import App
from DataImage import DataImage, ImageZone
from DataCaption import DataCaption
from ImageStore import ImageStore
import math
from Levenshtein import ratio
from tkinter import messagebox

image_store = ImageStore()

config = {
    'Main.ImageSize' : 700,
    'Main.DotRadius' : 10,
    'Vocab.GridDim' : (3,5),
    'Vocab.GridImageSize' : (150,150),
}

def inbetween(minv, val, maxv):
    return min(maxv, max(minv, val))

class Windows(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        # Adding a title to the window
        self.wm_title("Test Application")
        self.current_page = None
        
        # logic
        # test_data = r"K:\StableDiffusion\Train_Lora\Masafumi\Images\200_masaFrame"
        self.app = App()
        # self.app.read_folder(test_data)
        # self.app.load_json(test_data)
        # self.app.build_vocabulary()
        
        # creating menubar
        menu_bar = Menu(self)
        # File Menu
        menu_file = Menu(menu_bar, tearoff=0)
        menu_file.add_command(label="New...", command=self.new_archive, accelerator="Ctrl+N")
        menu_file.add_command(label="Open...", command=self.open_archive, accelerator="Ctrl+O")
        menu_file.add_command(label="Save", command=self.save_archive, accelerator="Ctrl+S")
        menu_file.add_command(label="Update Archive", command=self.update_archive, accelerator="Ctrl+U")
        menu_file.add_command(label="Create Flips", command=self.create_flips)
        menu_bar.add_cascade(label="File", menu=menu_file)
        # Caption Menu
        menu_file = Menu(menu_bar, tearoff=0)
        def cmd_goto() :
            if self.check_has_data() :
                self.open_popup(self.goto, "Go to ...", "Enter picture index or name part")
        def cmd_addword() :
            if self.check_has_data() :
                self.open_popup(self.add_word, "Add tag", "Enter a tag to add to every caption")
        def cmd_removeword() :
            if self.check_has_data() :
                self.open_popup(self.remove_word, "Remove tag", "Enter a tag to remove from every caption")
        menu_file.add_command(label="Goto", command=cmd_goto, accelerator="Ctrl+G")
        menu_file.add_command(label="Filter", command=self.todo, accelerator="Ctrl+F")
        menu_file.add_command(label="Add Tag", command=cmd_addword)
        menu_file.add_command(label="Replace Spaces", command=self.replace_spaces)
        menu_file.add_command(label="Auto Typo", command=self.auto_correct_typos)
        menu_file.add_command(label="Remove Tag", command=cmd_removeword)
        menu_file.add_command(label="Remove Picture", command=self.remove_picture)
        menu_bar.add_cascade(label="Caption", menu=menu_file)
        # Zone menu
        menu_file = Menu(menu_bar, tearoff=0)
        menu_file.add_command(label="Rename", command=self.rename_zone)
        menu_file.add_command(label="Remove", command=self.remove_zone)
        menu_bar.add_cascade(label="Zone", menu=menu_file)
        # View menu
        menu_file = Menu(menu_bar, tearoff=0)
        menu_file.add_command(label="Caption browser", command=lambda : self.show_frame(MainPage))
        menu_file.add_command(label="Vocabulary", command=lambda : self.show_frame(VocabPage))
        menu_bar.add_cascade(label="View", menu=menu_file)

        self.config(menu=menu_bar)
        
        self.bind('<Control-n>', lambda x : self.new_archive())
        self.bind('<Control-o>', lambda x : self.open_archive())
        self.bind('<Control-s>', lambda x : self.save_archive())
        self.bind('<Control-u>', lambda x : self.update_archive())
        
        self.bind('<Control-g>', lambda x : cmd_goto())
        self.bind('<Control-f>', lambda x : self.todo())
        
        self.bind('<Control-space>', lambda x : self.next_page())
        self.bind('<Control-Shift-space>', lambda x : self.prev_page())

        # bind zone selection
        def key_handler(event) :
            if event.keycode >= 48 and event.keycode <=57 \
                and event.state == 12 :
                zone_index = (event.keycode - 48 -1 ) % 10
                self.frames[MainPage].manual_zone_select(zone_index)
        self.bind("<Key>", key_handler)
        # TODO : reset captions
        # TODO : clean unused zones / remove zone manually
        # TODO : detected unimported files and broken paths -> synchronize files
        # TODO : vocab visualisation
        # TODO : vocab relations and analysis
        # TODO : Specific passes
        # TODO : rename zone
        # TODO : rename picture
        # TODO : redim zone
        # TODO : redim crop
        # TODO : filter set and remove
        # TODO : add tag at start of every file
        # TODO : replace tag

        # creating a frame and assigning it to container
        container = Frame(self, height=400, width=600)
        # specifying the region where the frame is packed in root
        container.pack(side="top", fill="both", expand=True)

        # configuring the location of the container using grid
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # We will now create a dictionary of frames
        self.frames = {}
        # we'll create the frames
        for F in [ VocabPage, MainPage ] :
            frame = F(container, self.app, self)
            self.frames[F] = frame
            frame.grid(row=1, column=0, sticky="nsew")

        # Method to switch frames
        self.show_frame(MainPage)
    
    def check_has_data(self) -> bool :
        hasdata = len(self.app.data) > 0
        if  not hasdata:
            print("No data available. Can't perform process")
        return hasdata
    
    def todo(self) :
        print("Function not implemented")
    
    def goto(self, index) :
        if index == None or index.isspace() :
            print("No provided search value. Can't perform search")
            return

        if type(index) == str and index.isdigit() :
            index = int(index, 10)
        if type(index) == int :
            if index >=0 and index < len(self.app.data) :
                self.set_page(self.app.data[index])
            else :
                print(f"Couldn't find index : {index}")
        else : #str
            index = index.lower()
            for d in self.app.data :
                if index in d.get_file_name().lower() :
                    self.set_page(d)
                    return
            print("Couldn't find : ", index)
        
    def show_frame(self, cont):
        frame = self.frames[cont]
        # raises the current frame to the top
        frame.tkraise()
        self.current_page = frame
        self.update_page_display()
    
    def update_page_display(self) :
        p = self.get_page()
        if p :
            self.set_page(p)
    
    def next_page(self) :
        if self.current_page and getattr(self.current_page, 'next_image', None) :
            self.current_page.next_image()

    def prev_page(self) :
        if self.current_page and getattr(self.current_page, 'prev_image', None) :
            self.current_page.prev_image()
    
    def set_page(self, data:DataImage) :
        if self.current_page and getattr(self.current_page, 'set_current_image', None) :
            self.current_page.set_current_image(data)
    
    def get_page(self) -> DataImage :
        if self.current_page and getattr(self.current_page, 'get_current_image', None) :
            return self.current_page.get_current_image()
        
    def new_archive(self) :
        try:
            image_store.reset()
            folder_selected = filedialog.askdirectory()
            self.app.read_folder(folder_selected)
            self.frames[MainPage].set_current_image(self.app.data[0])
            self.frames[VocabPage].set_current_image("")
            print("Import Archive Done")
        except Exception as e:
            print("Error during import : ", e)
        
    def open_archive(self) :
        folder_selected = filedialog.askdirectory()
        try :
            image_store.reset()
            self.app.load_json(folder_selected)
            self.frames[MainPage].set_current_image(self.app.data[0])
            self.frames[VocabPage].set_current_image("")
            print("Open Archive Done")
        except FileNotFoundError as e:
            print("File not Found during load : ", e)
        except Exception as e:
            print("Error during load : ", e)
        
    def save_archive(self) :
        try:
            self.app.save_json()
            print("Save Archive Done")
        except Exception as e:
            print("Error during save : ", e)
        
    def update_archive(self) :
        try:
            self.app.update_caption_files()
            print("Update Archive Done")
        except Exception as e:
            print("Error during update : ", e)
            
    def create_flips(self) :
        try :
            self.app.create_flips()
            print("Flip process Done")
        except Exception as e:
            print("Error during flip process : ", e)
    
    def add_word(self, new_word : str) :
        for forbidden in [",", ";"] :
            if forbidden in new_word :
                print(f"The new tag can't contain the '{forbidden}' symbol.")
                return
        
        # do add tag
        self.app.add_word(new_word)
        # refresh currently displayed data
        self.update_page_display()
        
        print("Add Tag Done : ", new_word)

    def remove_word(self, new_word : str) :
        for forbidden in [",", ";"] :
            if forbidden in new_word :
                print(f"The new tag can't contain the '{forbidden}' symbol.")
                return
        
        # do add tag
        self.app.remove_word(new_word)
        # refresh currently displayed data
        self.update_page_display()
        
        print("Remove Tag Done : ", new_word)
    
    def remove_picture(self) :
        p = self.frames[MainPage].get_current_image()
        if not p : return
        
        # get new file index
        index = self.app.data.index(p)
        if index +1 >= len(self.app.data) :
            index= len(self.app.data) - 1
        
        # Ask and remove
        answer = messagebox.askyesno(f"Remove Picture", f"Remove '{p.get_file_name()}' ?")
        if answer :
            self.app.remove_picture(p)
            # refresh currently displayed data
            self.set_page(self.app.data[index])
            self.app.build_vocabulary()
            print(f"removed '{p.get_file_name()}'")
    
    def check_zone_selected(self) :
        return self.current_page == self.frames[MainPage] and \
            self.frames[MainPage].current_zone != None
    
    def rename_zone(self) :
        if self.check_zone_selected() :
            def edit_zone_name(self, new_name:str) :
                self.frames[MainPage].current_zone.name = new_name
                self.frames[MainPage].update_zone_list_display()
                print("renamed zone ", new_name)
                
            self.open_popup(partial(edit_zone_name, self), "Rename Zone", "Enter a Zone Name")
        else :
            print("Can't Rename Zone : No zone selected")
    
    def remove_zone(self) :
        if self.check_zone_selected() :
            im = self.frames[MainPage].current_image_caption
            zo = self.frames[MainPage].current_zone
            im.zones.remove(zo)
            self.frames[MainPage].update_zone_list_display()
            print(f"remove zone {im.get_file_name()}::{zo.name}")
        else :
            print("Can't Remove Zone : No zone selected")
        
    def replace_spaces(self) :
        self.app.replace_spaces()
        # refresh currently displayed data
        self.update_page_display()
        print("Space Replacing Done")
    
    def auto_correct_typos(self) :
        found = []
        words = list(self.app.vocabulary.words.keys())
        for i in range(len(words)) :
            for j in range(i+1, len(words)) :
                if ratio(words[i], words[j]) >= 0.8 :
                    if self.app.vocabulary.words[words[j]] > self.app.vocabulary.words[words[i]] :
                        found.append((words[i], words[j]))
                    else :
                        found.append((words[j], words[i]))
        
        prop = 1
        for c in found :
            answer = messagebox.askyesnocancel(f"Change {prop:2}/{len(found):2}", f"Change '{c[0]}' to '{c[1]}' ?")
            prop  += 1
            if answer == None :
                break
            elif answer :
                self.app.replace(c[0], c[1])
        
        # reset vocabulary analysis (because of the 0 ponderations)
        self.app.build_vocabulary()


    def rename_cmd(self, old_word:str) :
        if not self.check_has_data() : return
        self.open_popup(partial(self.rename_word, old_word),
                        "Rename tag : "+old_word, "Enter the tag new name")

    def rename_word(self, old_word:str, new_word : str) :
        for forbidden in [",", ";"] :
            if forbidden in old_word :
                print(f"The old tag can't contain the '{forbidden}' symbol. ({old_word})")
                return
            if forbidden in new_word :
                print(f"The new tag can't contain the '{forbidden}' symbol. ({new_word})")
                return
        
        # do add tag
        self.app.replace(old_word, new_word)
        # refresh currently displayed data
        self.update_page_display()
        
        print(f"Rename Tag Done : {old_word} -> {new_word}")
    
    def open_popup(self, use_text, window_title:str="Message", window_message:str = "please enter text"):
        top= Toplevel(self)
        # top.geometry("750x250")
        top.title(window_title)
        Label(top, text= window_message, font=('Mistral 18 bold')).pack()
        text = Text(top, height=1)
        text.pack(padx=5, pady=10)
        frame = Frame(top)
        def confirmation(misc=None) :
            use_text(text.get('1.0', '2.0-1c').strip())
            top.destroy()
        confirm = Button(frame, text="OK", command=confirmation)
        confirm.pack(side='left')
        cancel = Button(frame, text="Cancel", command=lambda : top.destroy())
        cancel.pack(side='right')
        frame.pack(padx=0)
        top.update()
        # add offset
        win_x = int((self.winfo_screenwidth() - top.winfo_width()) /2)
        win_y = int((self.winfo_screenheight() - top.winfo_height()) /2)
        top.geometry(f'+{win_x}+{win_y}')
        text.focus_set()
        top.bind("<Return>", confirmation)
        top.bind("<Escape>", lambda x : top.destroy())


class MainPage(Frame):

    """Displayed image max dimensions"""
    image_size = config['Main.ImageSize']
    dot_radius = config['Main.DotRadius']
    create_crop_button_text = "Create crop"
    goto_crop_button_text = "Go to crop"
    goto_original_button_text = "Go to original"
    
    def __init__(self, parent, controller, main_window):
        Frame.__init__(self, parent)
        self.controller = controller
        self.l1 = None
        self.l2 = None
        self.image = None
        self.raw_image = None
        self.imagedata = None
        self.rectangle_origin = None
        self.current_image_caption = None
        self.current_zone = None
        self.zones_indicators = dict()
        self.rectangle = None
        self.zone_selected = False
        self.data = []
        
        self.general_text = Text(self, height=4)
        self.general_text.pack(padx=10, pady=10, side="top", fill='x')
        self.general_text.bind("<<Modified>>", self.general_text_modified)
        
        # Center zone
        
        workzone = Frame(self)
        workzone.pack(padx=10, pady=0, fill="both")
        
        self.canvas = Canvas(workzone, width = MainPage.image_size, height = MainPage.image_size,
                             cursor="tcross")
        self.canvas.pack(side="left", fill="both")
        self.canvas.bind("<Button-1>", self.canvas_leftclic)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_release_leftclic)
        self.canvas.bind("<Motion>", self.canvas_mouse_motion)
        self.canvas.bind("<Double-Button-1>", self.canvas_double_leftclic)

        self.zone_text = Text(workzone, width = 20)
        self.zone_text.pack(padx=10, pady=10, side="right", fill='y')
        self.zone_text.bind("<<Modified>>", self.zone_text_modified)

        self.zone_listbox = Listbox(workzone, height=6, selectmode= SINGLE)
        self.zone_listbox.pack(padx=10, pady=10, side="right", fill="y")
        self.zone_listbox.bind("<<ListboxSelect>>", self.zone_listbox_select)
        
        self.zone_listbox.bind("<FocusIn>", self.zonelist_focus_management)
        self.zone_text.bind("<FocusOut>", self.zonetext_focus_management)

        # Navigation bar
    
        bottom_frame = Frame(self)
        bottom_frame.pack(padx=60, pady=10, side="bottom", fill="both")
        
        self.prev_picture_button = Button(bottom_frame, text=" < ", command=self.prev_image)
        self.prev_picture_button.pack(side="left", fill='y')
        
        self.next_picture_button = Button(bottom_frame, text=" > ", command=self.next_image)
        self.next_picture_button.pack(side="left", fill='y')
        
        self.pict_label = Label(bottom_frame, text="Pictures")
        self.pict_label.pack(side="left", fill='y')
        
        self.crop_button = Button(bottom_frame, text=MainPage.create_crop_button_text, command=self.create_cropped_image)
        self.crop_button.pack(side="right", fill='y')
    
    # DATA UPDATE
    def get_current_image(self) :
        return self.current_image_caption
    
    def set_current_image(self, data:DataImage) :
        # lock the text events propagation
        self.zone_text.edit_modified(True)
        self.general_text.edit_modified(True)
        self.current_zone = None
        # reset widgets
        self.zone_listbox.delete(0,END)
        self.zone_text.delete('1.0', 'end')
        self.general_text.delete('1.0', 'end')
        # update variables and display
        self.current_image_caption = data
        self.display_image(data.filepath)
        self.general_text.insert(END, ', '.join(data.current_caption.words))
        # add every zone indicator
        self.update_zone_list_display()
        # unlock the text events
        self.zone_text.edit_modified(False)
        self.general_text.edit_modified(False)
        self.update_crop_button_text()
        self.general_text.focus()
        self.update_picture_label()
    
    def update_picture_label(self) :
        index = self.controller.data.index(self.current_image_caption)
        nbr = len(self.controller.data)
        self.pict_label['text'] = f"{index}/{nbr} - {self.current_image_caption.get_file_name()}"
    
    def add_zone(self, newZone:ImageZone) :
        self.zone_listbox.insert(END,newZone.name)

        # draw the selection dot
        point = self.get_canvas_pos(newZone.dim)
        r = MainPage.dot_radius
        dot = self.canvas.create_oval(point[0]-r, point[1]-r,
                                point[0]+r, point[1]+r,
                                fill='red')
        self.zones_indicators[point] = (newZone, dot)
        
        # if rectangle dimensions, also draw the entire zone
        if len(newZone.dim) == 4 :
            p2 = self.get_canvas_pos(newZone.dim[2:])
            self.canvas.create_rectangle(point[0], point[1],
                                         p2[0], p2[1],
                                         outline='red')
            
    def next_image(self) :
        if self.current_image_caption == None : return
        self.set_current_image(self.controller.next_image(self.current_image_caption))
    def prev_image(self) :
        if self.current_image_caption == None : return
        self.set_current_image(self.controller.prev_image(self.current_image_caption))
    
    # CANVAS LOGIC
    
    def display_image(self, imagepath : str) :
        # reset every shape
        self.canvas.delete('all')
        self.zones_indicators.clear()
        self.l1 = None
        self.l2 = None
    
        # compute dimensions of display
        self.raw_image = Image.open(imagepath)
        image = self.raw_image
        position = ImageStore.stretch_image(image, (MainPage.image_size, MainPage.image_size))
        if position[4] != 1.0 :
            image = image.resize(position[2:4], Image.Resampling.LANCZOS)
        
        # update image data and display
        self.image = image
        self.imagedata = position
        self.picture = ImageTk.PhotoImage(image)
        self.canvas.create_image(self.imagedata[0],
                                 self.imagedata[1],
                                 anchor=NW, image=self.picture)
    
    def canvas_double_leftclic(self, event) :
        if self.image == None : return
        
        
        # check if within picture
        if self.imagedata[0] > event.x or event.x > MainPage.image_size-self.imagedata[0] or \
           self.imagedata[1] > event.y or event.y > MainPage.image_size-self.imagedata[1] :
               return
        
        # convert
        p = self.get_image_pos((event.x,event.y))
        
        # Create a Dot Zone
        nbrZone = len(self.current_image_caption.zones)
        newZone = ImageZone(f"NewDot-{nbrZone}", p)
        self.current_image_caption.zones.append(newZone)
        self.add_zone(newZone)
        self.rectangle_origin = None
        self.manual_zone_select(END)

    def canvas_leftclic(self, event) :
        if self.image == None : return
        
        
        # check if click on zone indicator
        radius = MainPage.dot_radius
        idx = 0
        for k in self.zones_indicators.keys() :
            if abs(event.x - k[0]) < radius and abs(event.y - k[1]) < radius :
                self.manual_zone_select(idx)
                return
            idx += 1
        
        # or start drawing a rectangle
        self.rectangle_origin = (inbetween(self.imagedata[0], event.x, MainPage.image_size-self.imagedata[0]),
                                 inbetween(self.imagedata[1], event.y, MainPage.image_size-self.imagedata[1]))
        self.rectangle = None

    def canvas_release_leftclic(self, event) :
        if self.image == None  or self.rectangle_origin == None : return
        
        # compute reference points
        p0 = self.get_image_pos(self.rectangle_origin)
        p1 = (inbetween(self.imagedata[0], event.x, MainPage.image_size-self.imagedata[0]),
              inbetween(self.imagedata[1], event.y, MainPage.image_size-self.imagedata[1]))
        p1 = self.get_image_pos(p1)
        
        # it too close to the origin, is not a elegible zone (and probably a double-clic)
        d = 2*MainPage.dot_radius
        if abs(p0[0] - p1[0]) < d or \
           abs(p0[1] - p1[1]) < d :
               self.rectangle_origin = None
               self.canvas.delete(self.rectangle)
               return
           
       # Create rectangle zone
        nbrZone = len(self.current_image_caption.zones)
        # force origin on uper_left corner
        if p0[0] > p1[0] :
            swap = p0[0]
            p0 = (p1[0], p0[1])
            p1 = (swap , p1[1])
        if p0[1] > p1[1] :
            swap = p0[1]
            p0 = (p0[0], p1[1])
            p1 = (p1[0], swap )
        newZone = ImageZone(f"NewRect-{nbrZone}", (p0[0], p0[1], p1[0], p1[1]))
        self.current_image_caption.zones.append(newZone)
        self.add_zone(newZone)
        self.manual_zone_select(END)
        
        self.rectangle_origin = None
        self.canvas.delete(self.rectangle)

    def canvas_mouse_motion(self, event) :
        if self.image == None : return
        
        self.canvas.delete(self.l1)
        self.canvas.delete(self.l2)
        
        # if a rectangle is drawn,update rectangle preview
        if self.rectangle_origin :
            self.canvas.delete(self.rectangle)
            self.rectangle = self.canvas.create_rectangle(
                self.rectangle_origin[0],
                self.rectangle_origin[1], 
                inbetween(self.imagedata[0], event.x, MainPage.image_size-self.imagedata[0]),
                inbetween(self.imagedata[1], event.y, MainPage.image_size-self.imagedata[1]))
        # if nothing, draw cursor
        else :
            self.l1 = self.canvas.create_line(
                inbetween(self.imagedata[0], event.x, MainPage.image_size-self.imagedata[0]),
                self.imagedata[1],
                inbetween(self.imagedata[0], event.x, MainPage.image_size-self.imagedata[0]),
                MainPage.image_size-self.imagedata[1])
            self.l2 = self.canvas.create_line(
                self.imagedata[0],
                inbetween(self.imagedata[1], event.y, MainPage.image_size-self.imagedata[1]),
                MainPage.image_size-self.imagedata[0],
                inbetween(self.imagedata[1], event.y, MainPage.image_size-self.imagedata[1]))
    
    def get_image_pos(self, canvaspos) :
        return (int((canvaspos[0]-self.imagedata[0])/self.imagedata[4]),
                int((canvaspos[1]-self.imagedata[1])/self.imagedata[4]))
    def get_canvas_pos(self, imagepos) :
        return (int((imagepos[0]*self.imagedata[4]+self.imagedata[0])),
                int((imagepos[1]*self.imagedata[4]+self.imagedata[1])))
    
    # OTHER WIDGETS EVENTS

    def update_zone_list_display(self) :
        self.zone_listbox.delete(0,END)
        for zi in self.current_image_caption.zones :
            self.add_zone(zi)

    def manual_zone_select(self, zone_index:int) :
        if zone_index != END and zone_index >= self.zone_listbox.size() : return
        self.zone_listbox.selection_clear(0,END)
        self.zone_listbox.selection_set(zone_index)
        self.zone_listbox_select(None)

    def zone_listbox_select(self, event) :
        selected_indices = self.zone_listbox.curselection()
        if len(selected_indices) == 0:
            # self.current_zone = None
            self.crop_button['text'] = "X"
            return
        zone = self.current_image_caption.zones[selected_indices[0]]
        self.current_zone = None
        self.zone_text.delete('1.0', 'end')
        self.zone_text.insert(END, '\n'.join(zone.caption))
        self.current_zone = zone
        # TODO : change dot color of selected zone
        self.update_crop_button_text()
        self.zone_listbox.focus = False
        self.zone_text.focus()
        self.zone_selected = True
    
    def zonelist_focus_management(self, event) :
        if self.zone_selected:
            self.zone_text.focus()
            self.zone_selected = False
    
    def zonetext_focus_management(self, event) :
        # self.zone_selected = False
        # TODO : when changing focus manually from text to list, the action is canceled once.
        pass

    def update_crop_button_text(self) :
        if self.current_image_caption.original_image :
            self.crop_button['text'] = MainPage.goto_original_button_text
        elif not self.current_zone :
            self.crop_button['text'] = "X"
        elif self.current_zone.cropped_image :
            self.crop_button['text'] = MainPage.goto_crop_button_text
        else :
            self.crop_button['text'] = MainPage.create_crop_button_text
    
    def zone_text_modified(self, event) :
        if self.current_zone == None :
            self.zone_text.edit_modified(False)
            return
        t = self.zone_text.get('1.0', 'end')
        self.current_zone.caption = DataCaption.clean_text(t)
        self.zone_text.edit_modified(False)
    
    def general_text_modified(self, event) :
        if self.current_image_caption == None :
            self.general_text.edit_modified(False)
            return
        t = self.general_text.get('1.0', 'end')
        self.current_image_caption.current_caption = DataCaption.clean_text(t)
        self.general_text.edit_modified(False)
    
    def create_cropped_image(self) :
        # use current selected rectangle zone
        if (self.current_zone and len(self.current_zone.dim) == 4) or\
            self.current_image_caption.original_image:
            
            try :
                # go to the original
                if self.current_image_caption.original_image :
                    original = self.controller.find_data_by_filepath(self.current_image_caption.original_image)
                    self.set_current_image(original)
                # if doesn't already have a cropped image
                elif not self.current_zone.cropped_image :
                    fname, fextension = os.path.splitext(self.current_image_caption.filepath)
                    dimage = DataImage()
                    dimage.filepath = fname + "_" + self.current_zone.name + fextension
                    dimage.original_image = self.current_image_caption.filepath
                    dimage.current_caption.words = self.current_zone.caption.words.copy()
                    dimage.current_caption.append("close-up")
                    dimage.init_original_caption()
                    self.controller.add_data(dimage)
                    self.current_zone.cropped_image = dimage.filepath

                    # create new caption file
                    f = open(fname + "_" + self.current_zone.name + ".txt", "w")
                    f.write(dimage.current_caption.to_csv())
                    f.close()
                    # create new png file
                    crop = self.raw_image.crop(self.current_zone.dim)
                    crop.save(dimage.filepath, "PNG")
                    self.crop_button['text'] = MainPage.goto_crop_button_text
                # go to the cropped image
                else :
                    cropped = self.controller.find_data_by_filepath(self.current_zone.cropped_image)
                    self.set_current_image(cropped)
            except Exception as e:
                print("Error during cropping : ", e)
                raise e

class VocabPage(Frame):

    def __init__(self, parent, controller, main_window):
        Frame.__init__(self, parent)
        self.controller = controller
        self.main_window = main_window
        self.vocab_data = None
        self.selected_word = None
        self.alphasort = False
        self.filter_pattern = ""
        self.inhibit_vocab_scrollbar = None
        self.selected_correl = -1
        self.tagged_picts = None # DataImage[]
        self.untagged_picts = None # DataImage[]

        left_frame = Frame(self)
        left_frame.pack(padx=10, pady=10, side="left", fill="y")
        
        self.changesort_button = Button(left_frame, text="Frequency", command=self.change_sort)
        self.changesort_button.pack(side="top", fill='x', pady='5')
        
        self.search_filter = Text(left_frame, height = 1, width = 20)
        self.search_filter.pack(side='top', fill ='x')
        self.search_filter.bind("<<Modified>>", self.update_filter)
        
        vocab_scroll_frame = Frame(left_frame)
        vocab_scroll_frame.pack(padx=10, pady=10, fill="y", expand='true')
        
        self.vocab_list = Listbox(vocab_scroll_frame, width=30, selectmode= SINGLE)
        self.vocab_list.pack(padx=10, pady=10, side='left', fill="y", expand='true')
        self.vocab_list.bind("<<ListboxSelect>>", self.vocabword_select)
        self.vocab_scrollbar = Scrollbar(vocab_scroll_frame)
        self.vocab_scrollbar.pack(side='left', fill = 'y', expand='true')
        def scroll_bar_inhib_manage(x,y) :
            if self.inhibit_vocab_scrollbar :
                self.vocab_list.yview_moveto(self.inhibit_vocab_scrollbar[0])
                self.inhibit_vocab_scrollbar = None
                return
            self.vocab_scrollbar.set(x,y)
        self.vocab_list.config(yscrollcommand = scroll_bar_inhib_manage)
        self.vocab_scrollbar.config(command = self.vocab_list.yview)
        
        self.remove_button = Button(left_frame, text="Remove", command=self.remove_word)
        self.remove_button.pack(side="bottom", fill='x', pady='5')
        
        rename_button = Button(left_frame, text="Rename", command=self.rename_word)
        rename_button.pack(side="bottom", fill='x')
        
        mid_frame = Frame(self)
        mid_frame.pack(padx=10, pady=0, side="left", fill="y")

        self.correltitle_label = Label(mid_frame, height=4, text = "The words")
        self.correltitle_label.pack(padx=10, pady=10, side='top', fill="x")
        
        correl_frame = Frame(mid_frame)
        correl_frame.pack(expand ="true", fill='both')
        self.correl_list = Listbox(correl_frame, width=30, selectmode= SINGLE)
        self.correl_list.pack(padx=10, pady=10, side="left", fill="y")
        self.correl_list.bind("<<ListboxSelect>>", self.correl_select)
        correl_scrollbar = Scrollbar(correl_frame)
        correl_scrollbar.pack(side = 'left', fill = 'y')
        self.correl_list.config(yscrollcommand = correl_scrollbar.set)
        correl_scrollbar.config(command = self.correl_list.yview)
        
        # The display zone
        self.negatives = CanvasGrid(self, config['Vocab.GridDim'], config['Vocab.GridImageSize'])
        self.negatives.pack(side='right', fill="both")
        
        self.images = CanvasGrid(self, config['Vocab.GridDim'], config['Vocab.GridImageSize'])
        self.images.pack(side='right', fill="both")
        
        self.images.double_right_clic_event = self.on_tagged_picture_action
        self.negatives.double_right_clic_event = self.on_untagged_picture_action
        
        self.images.double_left_clic_event = self.on_picture_left_clic
        self.negatives.double_left_clic_event = self.on_picture_left_clic

        self.init_vocabulary()
    
    def on_picture_left_clic(self, event) :
        """Display caption of the picture"""
        self.main_window.show_frame(MainPage)
        self.main_window.set_page(event['picture'])
    
    def get_current_image(self) :
        """Doesn't have any image to update, but used for display update events from the main window"""
        return "a"
    
    def set_current_image(self, useless) :
        """Doesn't have any image to update, but used for display update events from the main window"""
        self.init_vocabulary()
    
    def init_vocabulary(self):
        self.controller.build_vocabulary()
        self.inhibit_vocab_scrollbar = self.vocab_scrollbar.get()
        self.vocab_list.delete(0, END)
        if self.alphasort :
            s = sorted(self.controller.vocabulary.words.items(), key=lambda x:x[0])
        else :
            s = sorted(self.controller.vocabulary.words.items(), key=lambda x:x[1])
            s.reverse()
        self.vocab_data = [w for w in s if w[1] != 0]
        if self.filter_pattern and not self.filter_pattern.isspace() :
            self.vocab_data = [w for w in self.vocab_data if re.search(self.filter_pattern, w[0])]
        for k,i in self.vocab_data :
            if i != 0 :
                self.vocab_list.insert(END, f"{i:3} - {k}")
    
    def change_sort(self) :
        self.alphasort = not self.alphasort
        if self.alphasort :
            self.changesort_button['text'] = "Alphanum"
        else :
            self.changesort_button['text'] = "Frequency"
        self.init_vocabulary()
    
    def update_filter(self, event) :
        self.filter_pattern = self.search_filter.get("1.0", "2.0-1c")
        self.filter_pattern = re.sub("[\[\]]", "", self.filter_pattern)
        self.init_vocabulary()
        self.search_filter.edit_modified(False)
    
    def vocabword_select(self, event) :
        # get selection if any
        selected_indices = self.vocab_list.curselection()
        if len(selected_indices) == 0:
            return
        word = self.vocab_data[selected_indices[0]]
        
        self.remove_button['text'] = f"Remove '{word[0]}'"
        
        # display the selected word correlations
        self.update_correlations(word[0])
    
    def update_correlations(self, word) :
        self.selected_word = word
        self.selected_tag_set = word
        pond = self.controller.vocabulary.words[word]
        self.correltitle_label['text'] = f"{word} - {pond}/{len(self.controller.data)}"
        
        # pictures using the word as a tag
        self.tagged_picts = [d for d in self.controller.data if d.contains(word)]
        self.untagged_picts = [d for d in self.controller.data if not d.contains(word)]
        
        # find correlations
        self.correl_data = []
        for w in self.vocab_data :
            if w[0] == word : continue
            
            counter = 0
            for d in self.tagged_picts :
                if d.contains(w[0]) :
                       counter += 1
            # if counter > 0:
            self.correl_data.append((w[0], w[1], counter))
        
        # sort and display correlations
        self.correl_list.delete(0, END)
        self.correl_data = sorted(self.correl_data, key=lambda x:x[2])
        self.correl_data.reverse()
        for c in self.correl_data :
            self.correl_list.insert(END, f"{c[2]:3}/{c[1]:3} - {c[0]}")
        
        # display tagged images
        self.images.set_gallery(self.tagged_picts)
        self.negatives.set_gallery(self.untagged_picts)

    def correl_select(self, event) :
        # get selection if any
        selected_correl = self.correl_list.curselection()
        if len(selected_correl) == 0:
            self.selected_correl = -1
            return
        selected_correl = selected_correl[0]
        correl_word = self.correl_data[selected_correl][0]
        
        # if clicked on the item for the second time
        if self.selected_correl == selected_correl :
            # use selected item as new displayed correlation
            self.selected_correl = -1
            self.update_correlations(correl_word)
            return
        # save selected index for next selection
        self.selected_correl = selected_correl

        self.selected_tag_set = correl_word
        # pictures using the word as a tag
        tagged = [d for d in self.tagged_picts if d.contains(correl_word)]
        untagged = [d for d in self.tagged_picts if not d.contains(correl_word)]
        
        # display tagged and untagged images
        self.images.set_gallery(tagged)
        self.negatives.set_gallery(untagged)

    def on_tagged_picture_action(self, event) :
        tag = self.selected_tag_set
        pict = event["picture"]
        self.images.remove_from_gallery(pict)
        self.negatives.add_to_gallery(pict)
        pict.remove_tag(tag)
        self.controller.vocabulary.dec_word(tag)
        self.init_vocabulary()
        print(f"remove tag '{tag}' from picture {pict.get_file_name()}")
    
    def on_untagged_picture_action(self, event) :
        tag = self.selected_tag_set
        pict = event["picture"]
        self.negatives.remove_from_gallery(pict)
        self.images.add_to_gallery(pict)
        pict.current_caption.append(tag)
        self.controller.vocabulary.add_word(tag)
        self.init_vocabulary()
        print(f"add tag '{tag}' to picture {pict.get_file_name()}")
    
    def rename_word(self) :
        self.main_window.rename_cmd(self.selected_word)

    def remove_word(self) :
        self.main_window.remove_word(self.selected_word)

class CanvasGrid(Frame) :
    def __init__(self, parent, grid_dim, image_dim) :
        Frame.__init__(self, parent)
        self.pictures = None
        self.double_right_clic_event = None
        self.double_left_clic_event = None
        
        dim = (4,7) #col/row
        self.grid_dim = grid_dim
        self.image_dim = image_dim
        
        scroll_frame = Frame(self)
        scroll_frame.pack(padx=10, pady=0, side='right', fill="both")
        
        up_button = Button(scroll_frame, text=' ^ ', command=partial(self.scroll_up, self.grid_dim[1]))
        up_button.pack(side='top', fill="x")
        
        workzone = Frame(scroll_frame, width = grid_dim[0]*image_dim[0], height = grid_dim[1]*image_dim[1])
        workzone.pack(padx=10, pady=0, fill="both", expand = 'true')
        
        self.grid_canvas = []# [row][col]
        self.grid_images = []# [row][col]
        for j in range(0,grid_dim[1]) : # each row
            self.grid_canvas.append([])
            self.grid_images.append([])
            for i in range(0,grid_dim[0]) : # each column
                nc = Canvas(workzone, width=image_dim[0], height=image_dim[1])
                self.grid_canvas[j].append(nc)
                self.grid_images[j].append(None)
                nc.grid(column=i, row=j)
                
                def stretch(self, col, row, event) :
                    im = self.get_picture(col, row)
                    if im :
                        im = Image.open(im.filepath)
                        self.zoom_magnifying(im)
                def remove_magnifying(self, event) :
                    self.overlap_canvas.place_forget()
                def on_mouse_double_left_clic_event(self, col, row, event) :
                    if self.double_left_clic_event :
                        pict = self.get_picture(col, row)
                        if pict :
                            self.double_left_clic_event({"canvas"  : self,
                                                          "picture" : pict})
                def on_mouse_double_right_clic_event(self, col, row, event) :
                    if self.double_right_clic_event :
                        pict = self.get_picture(col, row)
                        if pict :
                            self.double_right_clic_event({"canvas"  : self,
                                                          "picture" : pict})
                nc.bind("<ButtonPress-2>", partial(stretch, self, j,i))
                nc.bind("<ButtonRelease-2>", partial(remove_magnifying, self))
                nc.bind("<Double-Button-1>", partial(on_mouse_double_left_clic_event, self, j,i))
                nc.bind("<Double-Button-3>", partial(on_mouse_double_right_clic_event, self, j,i))
                
        down_button = Button(scroll_frame, text=' \\/ ', command=partial(self.scroll_down, self.grid_dim[1]))
        down_button.pack(side='bottom', fill="x")
        
        self.bind('<Enter>', self._bound_to_mousewheel)
        self.bind('<Leave>', self._unbound_to_mousewheel)
        
        self.magnify_dim = (600, 600)
        self.overlap_canvas = Canvas(self, width = self.magnify_dim[0], height = self.magnify_dim[1])
    
    def _bound_to_mousewheel(self, event):
        self.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _unbound_to_mousewheel(self, event):
        self.unbind_all("<MouseWheel>")
    
    def _on_mousewheel(self, event):
        if event.delta > 0 :
            self.scroll_up(self.grid_dim[1])
        else :
            self.scroll_down(self.grid_dim[1])
    
    def get_picture(self, row, col) :
        index = self.grid_dim[0]*(self.gallery_index + row)+col
        if index >= len(self.pictures) :
            return None
        return self.pictures[index]
    
    def get_max_picture_count(self) :
        return self.grid_dim[0] * self.grid_dim[1]
    
    def clear_all(self) :
        for r in self.grid_canvas :
            for can in r:
                can.delete('all')
    
    def set_gallery(self, pictures : list[DataImage]) :
        self.pictures = pictures
        self.gallery_index = 0
        self.update_gallery(0, self.get_max_picture_count())

    def is_displayed(self, index) :
        return self.gallery_index * self.grid_dim[0] <= index and \
               self.gallery_index * self.grid_dim[0] + self.get_max_picture_count() > index
    
    def add_to_gallery(self, picture) :
        self.pictures.append(picture)
        new_index = len(self.pictures) - 1
        if self.is_displayed(new_index) :
            self.update_gallery(new_index, new_index+1)
    
    def remove_from_gallery(self, picture) :
        index = self.pictures.index(picture)
        self.pictures.remove(picture)
        if self.is_displayed(index) :
            self.update_gallery(index,self.gallery_index * self.grid_dim[0] + self.get_max_picture_count())
    
    def scroll_up(self, inc:int = 1) :
        if not self.pictures or len(self.pictures) <= self.get_max_picture_count() :
            return
        if self.gallery_index == 0 :
            return
        self.gallery_index = max(0, self.gallery_index - inc)
        self.update_gallery(self.gallery_index * self.grid_dim[0],
                            self.gallery_index * self.grid_dim[0] + self.get_max_picture_count())

    def scroll_down(self, inc:int = 1) :
        if not self.pictures or len(self.pictures) <= self.get_max_picture_count() :
            return
        max_index = math.ceil(len(self.pictures) / self.grid_dim[0]) - self.grid_dim[1]
        if self.gallery_index == max_index :
            return
        self.gallery_index = min(max_index, self.gallery_index + inc)
        self.update_gallery(self.gallery_index * self.grid_dim[0],
                            self.gallery_index * self.grid_dim[0] + self.get_max_picture_count())

    def update_gallery(self, start, stop) :
        for im_counter in range(start, stop) :
            if im_counter < len(self.pictures) :
                # raw_image = Image.open(self.pictures[im_counter].filepath)
                self.display_image_at(self.pictures[im_counter], im_counter)
            else :
                self.display_image_at(None, im_counter)
    
    def display_image_at(self, im:DataImage, col:int, row:int=None) :
        if row == None :
            col, row = col%self.grid_dim[0], int(col/self.grid_dim[0]) - self.gallery_index
        c = self.grid_canvas[row][col]
        
        # reset every shape
        c.delete('all')
        
        if im == None :
            return
        
        mini, position = image_store.ask(im.filepath, self.image_dim)
        self.grid_images[row][col] = mini
        c.create_image(position[0], position[1],
                        anchor=NW,
                        image=self.grid_images[row][col])
    
    def zoom_magnifying(self, im:Image) :
        # print(self.winfo_width(), self.magnify_dim[0], self.winfo_x())
        # print(self.winfo_height(), self.magnify_dim[1], self.winfo_y())
        self.overlap_canvas.delete('all')
        
        position = ImageStore.stretch_image(im, self.magnify_dim)
        if position[4] != 1.0 :
            im = im.resize(position[2:4], Image.Resampling.LANCZOS)
        self.im = ImageTk.PhotoImage(im)# only for keeping reference
        self.overlap_canvas['width'] = position[2]
        self.overlap_canvas['height'] = position[3]
        self.overlap_canvas.create_image(
                        1,1,
                        # position[0], position[1],
                        anchor=NW,
                        image=self.im)
        pos = (
            (self.winfo_width()  - self.magnify_dim[0])/2,
            (self.winfo_height() - self.magnify_dim[1])/2)
        self.overlap_canvas.place(x=pos[0] + position[0], y=pos[1] + position[1])
        
    def zoom_popup(self, im:Image):
        top = Toplevel(self)
        top.geometry("800x800")
        top.title("Picture Display")
        position = ImageStore.stretch_image(im, (800,800))
        if position[4] != 1.0 :
            im = im.resize(position[2:4], Image.Resampling.LANCZOS)
        self.im = ImageTk.PhotoImage(im)# only for keeping reference
        c = Canvas(top)
        c.pack(fill='both', expand='true')
        c.create_image(position[0], position[1],
                        anchor=NW,
                        image=self.im) # TODO probably 

if __name__ == "__main__" :
    w = Windows()
    w.mainloop()
