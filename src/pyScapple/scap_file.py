"""Provide a class for Scapple file representation.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import xml.etree.ElementTree as ET

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

        Yw7File.__init__(self, filePath, **kwargs)
        self.exportScenes = kwargs['export_scenes']
        self.exportCharacters = kwargs['export_characters']
        self.exportLocations = kwargs['export_locations']
        self.exportItems = kwargs['export_items']

    def read(self):
        """Parse the Scapple xml file, fetching the Novel attributes.
        Create an object structure of Scapple notes.
        Return a message beginning with SUCCESS or ERROR.
        Override the superclass method.
        """

        try:
            self.tree = ET.parse(self.filePath)

        except:
            return 'ERROR: Can not process "' + os.path.normpath(self.filePath) + '".'

        root = self.tree.getroot()

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

                if self.exportScenes:
                    scene = Scene()
                    scene.title = note.text
                    scene.isNotesScene = note.isNotesScene
                    scene.status = 1
                    # Status = Outline

                    self.scenes[note.uid] = scene

            elif note.isMajorChara:

                if self.exportCharacters:
                    character = Character()
                    character.title = note.text
                    character.fullName = note.text
                    character.isMajor = True
                    self.characters[note.uid] = character
                    self.srtCharacters.append(note.uid)

            elif note.isMinorChara:

                if self.exportCharacters:
                    character = Character()
                    character.title = note.text
                    character.fullName = note.text
                    character.isMajor = False
                    self.characters[note.uid] = character
                    self.srtCharacters.append(note.uid)

            elif note.isLocation:

                if self.exportLocations:
                    location = WorldElement()
                    location.title = note.text
                    self.locations[note.uid] = location
                    self.srtLocations.append(note.uid)

            elif note.isItem:

                if self.exportItems:
                    item = WorldElement()
                    item.title = note.text
                    self.items[note.uid] = item
                    self.srtItems.append(note.uid)

        #--- Sort notes by position.

        srtNotes = sorted(uidByPos.items())

        for srtNote in srtNotes:
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

        return 'SUCCESS'

    def yw_to_scapple(self):
        """Convert the yWriter elements into Scapple notes.
        """
        scapNotes = {}
        tags = {}
        characters = {}
        locations = {}
        items = {}
        noteUid = 0

        for chId in self.srtChapters:

            for scId in self.chapters[chId].srtScenes:
                sceneNote = ScapNote()
                sceneNote.uid = noteUid
                noteUid += 1
                sceneNote.text = self.scenes[scId].title
                sceneNote.isScene = True
                sceneNote.isNotesScene = self.scenes[scId].isNotesScene
                sceneNote.isTag = False
                sceneNote.isNote = False
                sceneNote.isMajorChara = False
                sceneNote.isMinorChara = False
                sceneNote.isLocation = False
                sceneNote.isItem = False
                sceneNote.connections = []
                sceneNote.pointTo = []

                if self.scenes[scId].notes:
                    noteNote = ScapNote()
                    noteNote.uid = noteUid
                    noteUid += 1
                    noteNote.text = self.scenes[scId].notes
                    noteNote.isScene = False
                    noteNote.isNotesScene = False
                    noteNote.isTag = False
                    noteNote.isNote = True
                    noteNote.isMajorChara = False
                    noteNote.isMinorChara = False
                    noteNote.isLocation = False
                    noteNote.isItem = False
                    noteNote.connections = [sceneNote.uid]
                    sceneNote.connections.append(noteNote.uid)
                    noteNote.pointTo = []
                    scapNotes[noteNote.uid] = noteNote

                for tag in self.scenes[scId].tags:

                    if not tag in tags:
                        tagNote = ScapNote()
                        tagNote.uid = noteUid
                        noteUid += 1
                        tags[tag] = tagNote.uid
                        tagNote.text = tag
                        tagNote.isScene = False
                        tagNote.isNotesScene = False
                        tagNote.isTag = True
                        tagNote.isNote = False
                        tagNote.isMajorChara = False
                        tagNote.isMinorChara = False
                        tagNote.isLocation = False
                        tagNote.isItem = False
                        tagNote.connections = [sceneNote.uid]
                        sceneNote.connections.append(tagNote.uid)
                        tagNote.pointTo = []
                        scapNotes[tagNote.uid] = tagNote

                    else:
                        sceneNote.connections.append(tags[tag])
                        scapNotes[tags[tag]].connections.append(sceneNote.uid)

                for crId in self.scenes[scId].characters:

                    if not self.characters[crId].title in characters:
                        chrNote = ScapNote()
                        chrNote.uid = noteUid
                        noteUid += 1
                        characters[self.characters[crId].title] = chrNote.uid
                        chrNote.text = self.characters[crId].title
                        chrNote.isScene = False
                        chrNote.isNotesScene = False
                        chrNote.isTag = False
                        chrNote.isNote = False
                        chrNote.isMajorChara = self.characters[crId].isMajor
                        chrNote.isMinorChara = not self.characters[crId].isMajor
                        chrNote.isLocation = False
                        chrNote.isItem = False
                        chrNote.connections = [sceneNote.uid]
                        sceneNote.connections.append(chrNote.uid)
                        chrNote.pointTo = []
                        scapNotes[chrNote.uid] = chrNote

                    else:
                        sceneNote.connections.append(characters[self.characters[crId].title])
                        scapNotes[characters[self.characters[crId].title]].connections.append(sceneNote.uid)

                for lcId in self.scenes[scId].locations:

                    if not self.locations[lcId].title in locations:
                        locNote = ScapNote()
                        locNote.uid = noteUid
                        noteUid += 1
                        locations[self.locations[lcId].title] = locNote.uid
                        locNote.text = self.locations[lcId].title
                        locNote.isScene = False
                        locNote.isNotesScene = False
                        locNote.isTag = False
                        locNote.isNote = False
                        locNote.isMajorChara = False
                        locNote.isMinorChara = False
                        locNote.isLocation = True
                        locNote.isItem = False
                        locNote.connections = [sceneNote.uid]
                        sceneNote.connections.append(locNote.uid)
                        locNote.pointTo = []
                        scapNotes[locNote.uid] = locNote

                    else:
                        sceneNote.connections.append(locations[self.locations[lcId].title])
                        scapNotes[locations[self.locations[lcId].title]].connections.append(sceneNote.uid)

                for itId in self.scenes[scId].items:

                    if not self.items[itId].title in items:
                        itmNote = ScapNote()
                        itmNote.uid = noteUid
                        noteUid += 1
                        items[self.items[itId].title] = itmNote.uid
                        itmNote.text = self.items[itId].title
                        itmNote.isScene = False
                        itmNote.isNotesScene = False
                        itmNote.isTag = False
                        itmNote.isNote = False
                        itmNote.isMajorChara = False
                        itmNote.isMinorChara = False
                        itmNote.isLocation = False
                        itmNote.isItem = True
                        itmNote.connections = [sceneNote.uid]
                        sceneNote.connections.append(itmNote.uid)
                        itmNote.pointTo = []
                        scapNotes[itmNote.uid] = itmNote

                    else:
                        sceneNote.connections.append(items[self.items[itId].title])
                        scapNotes[items[self.items[itId].title]].connections.append(sceneNote.uid)

                scapNotes[sceneNote.uid] = sceneNote

    def write(self):
        """Create a new Scapple XML file located at filePath.
        Return a message beginning with SUCCESS or ERROR.
        Override the superclass method.
        """
