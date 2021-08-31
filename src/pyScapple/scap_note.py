"""Provide a class for Scapple note representation.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/scappex
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""


class ScapNote():
    """Scapple note representation.
    """

    Y_FACTOR = 100000
    # Sortable position = y * Y_FACTOR + x
    # This works if x and y are not greater than 9999.9

    def __init__(self, xmlNote):
        """Parse a single Scapple note.
        Extend the superclass method.
        """
        self.isScene = False
        self.isNotesScene = False
        self.isTag = False
        self.isNote = False
        self.color = ''

        self.text = xmlNote.find('String').text

        positionStr = xmlNote.attrib['Position'].split(',')
        self.position = float(positionStr[1]) * self.Y_FACTOR + float(positionStr[0])

        # Set UID.
        # Because Scapple UIDs begin with zero, they are all incremented by 1 for yWriter use.

        scappId = xmlNote.attrib['ID']
        self.uid = str(int(scappId) + 1)

        appearance = xmlNote.find('Appearance')
        color = appearance.find('TextColor')

        if color is not None:
            self.color = color.text

        border = appearance.find('Border')

        if border is not None:
            borderStyle = border.attrib['Style']

        else:
            borderStyle = ''

        if 'Shadow' in xmlNote.attrib:
            self.isScene = True

            if borderStyle == 'Cloud':
                self.isNotesScene = True

        elif borderStyle == 'Square':
            self.isTag = True

        elif borderStyle == 'Cloud':
            self.isNote = True

        # Create a list of connected notes.

        self.connections = []

        if xmlNote.find('ConnectedNoteIDs') is not None:
            connGroups = xmlNote.find('ConnectedNoteIDs').text.split(', ')

            for connText in connGroups:

                if '-' in connText:
                    conns = connText.split('-')
                    start = int(conns[0]) + 1
                    end = int(conns[1]) + 2

                    for i in range(start, end):
                        self.connections.append(str(i))

                else:
                    i = int(connText) + 1
                    self.connections.append(str(i))

        # Create a list of notes pointed to.

        self.pointTo = []

        if xmlNote.find('PointsToNoteIDs') is not None:
            pointGroups = xmlNote.find('PointsToNoteIDs').text.split(', ')

            for pointText in pointGroups:

                if '-' in pointText:
                    points = pointText.split('-')
                    start = int(points[0]) + 1
                    end = int(points[1]) + 2

                    for i in range(start, end):
                        self.pointTo.append(str(i))

                else:
                    i = int(pointText) + 1
                    self.pointTo.append(str(i))
