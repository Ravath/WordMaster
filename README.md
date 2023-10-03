# WordMaster

Word Master is a GUI application for managing the training data of text2image models.
 - Displays image and caption
 - Manages image area description and crops
 - Vocabulary analysis and management

# Dependencies

python modules :
 - tkinter
 - Levenshtein
 - PIL

# Run

python AppGui.py

# Usage

File > New  : Select a new folder containing training data (pictures + caption file)
	The data will be imported as new
File > Save : Saves the imported data as a save.json file
File > Open : Select a folder containing a save.json file to be loaded.
File > Update Archive : Update the caption files with the new data.
File > Create Flips : Create filpped images with the associated caption file.
	The flipped files are suffixed _flip, and will never be imported by WordMaster.

Caption > Goto : enter the index of a picture to go to, or use a search pattern
Caption > Filter : not implemented
Caption > Replace Tag : Replace every occurence of the given Tag with another one
Caption > Replace Spaces : Replace every spaces with '_'
Caption > Auto Typo : search for typos by comparing with similar words already used in the caption files, and suggest replacements
Caption > Remove Tag : Remove avery occurence of the given Tag
Caption > Remove Picture : Remove the current Picture from the data

Zone > Rename : Rename the current zone
Zone > Remove : Delete the current zone

