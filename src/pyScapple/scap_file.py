"""Provide a class for Scapple file representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import xml.etree.ElementTree as ET

from pywriter.pywriter_globals import ERROR
from pywriter.yw.yw7_file import Yw7File
from pywriter.model.chapter import Chapter
from pywriter.model.scene import Scene
from pywriter.model.character import Character
from pywriter.model.world_element import WorldElement

from pyScapple.scap_note import ScapNote


class ScapFile(Yw7File):
    """File representation of a Scapple file. 

    Represents a scap file containing an outline according to the conventions.
    - Scenes are shadowed.
    - Characters/locations/items are textColor-coded.
    """

    EXTENSION = '.scap'
    DESCRIPTION = 'Scapple diagram'
    SUFFIX = ''

    # Events assigned to the "narrative arc" (case insensitive) become
    # regular scenes, the others become Notes scenes.

    def __init__(self, filePath, **kwargs):
        """Extend the superclass constructor,
        defining instance variables.
        """
        ScapNote.locationColor = kwargs['location_color']
        ScapNote.itemColor = kwargs['item_color']
        ScapNote.majorCharaColor = kwargs['major_chara_color']
        ScapNote.minorCharaColor = kwargs['minor_chara_color']

        super().__init__(filePath, **kwargs)
        self._exportScenes = kwargs['export_scenes']
        self._exportCharacters = kwargs['export_characters']
        self._exportLocations = kwargs['export_locations']
        self._exportItems = kwargs['export_items']

    def read(self):
        """Parse the Scapple xml file, fetching the Novel attributes.
        Create an object structure of Scapple notes.
        Return a message beginning with the ERROR constant in case of error.
        Override the superclass method.
        """

        try:
            self._tree = ET.parse(self.filePath)

        except:
            return f'{ERROR}Can not process "{os.path.normpath(self.filePath)}".'

        root = self._tree.getroot()

        #--- Create a single chapter and assign all scenes to it.

        chId = '1'
        self.chapters[chId] = Chapter()
        self.chapters[chId].title = 'Chapter 1'
        self.srtChapters = [chId]

        #--- Parse Scapple notes.

        scapNotes = {}
        uidByPos = {}

        for xmlNote in root.iter('Note'):
            note = ScapNote()
            note.parse_xml(xmlNote)
            scapNotes[note.uid] = note
            uidByPos[note.position] = note.uid

            # Create Novel elements.

            if note.isScene:

                if self._exportScenes:
                    scene = Scene()
                    scene.title = note.text
                    scene.isNotesScene = note.isNotesScene
                    scene.status = 1
                    # Status = Outline

                    self.scenes[note.uid] = scene

            elif note.isMajorChara:

                if self._exportCharacters:
                    character = Character()
                    character.title = note.text
                    character.fullName = note.text
                    character.isMajor = True
                    self.characters[note.uid] = character
                    self.srtCharacters.append(note.uid)

            elif note.isMinorChara:

                if self._exportCharacters:
                    character = Character()
                    character.title = note.text
                    character.fullName = note.text
                    character.isMajor = False
                    self.characters[note.uid] = character
                    self.srtCharacters.append(note.uid)

            elif note.isLocation:

                if self._exportLocations:
                    location = WorldElement()
                    location.title = note.text
                    self.locations[note.uid] = location
                    self.srtLocations.append(note.uid)

            elif note.isItem:

                if self._exportItems:
                    item = WorldElement()
                    item.title = note.text
                    self.items[note.uid] = item
                    self.srtItems.append(note.uid)

        #--- Sort notes by position.

        srtNotes = sorted(uidByPos.items())

        for srtNote in srtNotes:

            if srtNote[1] in self.scenes:
                self.chapters[chId].srtScenes.append(srtNote[1])

        #--- Assign characters/locations/items/tags/notes to the scenes.

        for scId in self.scenes:
            self.scenes[scId].characters = []
            self.scenes[scId].locations = []
            self.scenes[scId].items = []
            self.scenes[scId].tags = []
            self.scenes[scId].sceneNotes = ''

            for uid in scapNotes[scId].connections:

                if uid in self.characters:

                    if scId in scapNotes[uid].pointTo:
                        self.scenes[scId].characters.insert(0, uid)

                    else:
                        self.scenes[scId].characters.append(uid)

                elif uid in self.locations:
                    self.scenes[scId].locations.append(uid)

                elif uid in self.items:
                    self.scenes[scId].items.append(uid)

                elif scapNotes[uid].isTag:
                    self.scenes[scId].tags.append(scapNotes[uid].text)

                elif scapNotes[uid].isNote:
                    self.scenes[scId].sceneNotes += scapNotes[uid].text

        #--- Assign tags/notes to the characters.

        for crId in self.characters:
            self.characters[crId].tags = []
            self.characters[crId].notes = ''

            for uid in scapNotes[crId].connections:

                if scapNotes[uid].isTag:
                    self.characters[crId].tags.append(scapNotes[uid].text)

                elif scapNotes[uid].isNote:
                    self.characters[crId].notes += scapNotes[uid].text

        #--- Assign tags to the locations.

        for lcId in self.locations:
            self.locations[lcId].tags = []

            for uid in scapNotes[lcId].connections:

                if scapNotes[uid].isTag:
                    self.locations[lcId].tags.append(scapNotes[uid].text)

        #--- Assign tags to the items.

        for itId in self.items:
            self.items[itId].tags = []

            for uid in scapNotes[itId].connections:

                if scapNotes[uid].isTag:
                    self.items[itId].tags.append(scapNotes[uid].text)

        return 'Scapple data converted to novel structure.'
