"""Provide a Scapple converter class for yWriter projects. 

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/scappex
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os

from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.yw.yw7_file import Yw7File
from pywriter.yw.data_files import DataFiles

from pyScapple.scap_file import ScapFile


class ScapConverter(YwCnvUi):
    """A converter class for Scapple diagram import."""

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.
        Override the superclass method.
        """
        self.newFile = None

        if not os.path.isfile(sourcePath):
            self.ui.set_info_how('ERROR: File "' + os.path.normpath(sourcePath) + '" not found.')
            return

        fileName, fileExtension = os.path.splitext(sourcePath)

        if fileExtension == ScapFile.EXTENSION:
            sourceFile = ScapFile(sourcePath, **kwargs)

            if os.path.isfile(fileName + Yw7File.EXTENSION):
                targetFile = DataFiles(fileName + DataFiles.EXTENSION, **kwargs)
                self.import_to_yw(sourceFile, targetFile)

            else:
                targetFile = Yw7File(fileName + Yw7File.EXTENSION, **kwargs)
                self.create_yw7(sourceFile, targetFile)

        else:
            self.ui.set_info_how('ERROR: File type of "' + os.path.normpath(sourcePath) + '" not supported.')
