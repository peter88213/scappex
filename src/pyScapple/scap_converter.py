"""Provide a Scapple converter class for yWriter projects. 

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.converter.new_project_factory import NewProjectFactory

from pyScapple.scap_file import ScapFile


class ScapConverter(YwCnvUi):
    """A converter class for csv timeline import."""
    CREATE_SOURCE_CLASSES = [ScapFile]

    def __init__(self):
        YwCnvUi.__init__(self)
        self.newProjectFactory = NewProjectFactory(self.CREATE_SOURCE_CLASSES)