""" Regression test for the scappex project.

Test suite for scappex.pyw.

For further information see https://github.com/peter88213/scappex
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from shutil import copyfile
import os
import unittest
import scappex_


# Test environment

# The paths are relative to the "test" directory,
# where this script is placed and executed

TEST_PATH = os.getcwd() + '/../test'
TEST_DATA_PATH = TEST_PATH + '/data/'
TEST_EXEC_PATH = TEST_PATH + '/yw7/'

# To be placed in TEST_DATA_PATH:
NORMAL_YW7 = TEST_DATA_PATH + 'normal.yw7'
NORMAL_SCAP = TEST_DATA_PATH + 'normal.scap'
NORMAL_CHARACTERS_XML = TEST_DATA_PATH + 'normal_Characters.xml'
NORMAL_LOCATIONS_XML = TEST_DATA_PATH + 'normal_Locations.xml'
NORMAL_ITEMS_XML = TEST_DATA_PATH + 'normal_Items.xml'
INI_FILE = 'scappex.ini'

# Test data
TEST_YW7 = TEST_EXEC_PATH + 'yw7 Sample Project.yw7'
TEST_SCAP = TEST_EXEC_PATH + 'yw7 Sample Project.scap'
TEST_CHARACTERS_XML = TEST_EXEC_PATH + 'yw7 Sample Project_Characters.xml'
TEST_LOCATIONS_XML = TEST_EXEC_PATH + 'yw7 Sample Project_Locations.xml'
TEST_ITEMS_XML = TEST_EXEC_PATH + 'yw7 Sample Project_Items.xml'


def read_file(inputFile):
    try:
        with open(inputFile, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        # HTML files exported by a word processor may be ANSI encoded.
        with open(inputFile, 'r') as f:
            return f.read()


def remove_all_testfiles():

    try:
        os.remove(TEST_YW7)

    except:
        pass

    try:
        os.remove(TEST_SCAP)
    except:
        pass

    try:
        os.remove(TEST_EXEC_PATH + INI_FILE)
    except:
        pass

    try:
        os.remove(TEST_CHARACTERS_XML)
    except:
        pass

    try:
        os.remove(TEST_LOCATIONS_XML)
    except:
        pass

    try:
        os.remove(TEST_ITEMS_XML)
    except:
        pass


class NormalOperation(unittest.TestCase):
    """Test case: Normal operation."""

    def setUp(self):

        try:
            os.mkdir(TEST_EXEC_PATH)

        except:
            pass

        remove_all_testfiles()

    def test_scap_to_new_yw(self):
        copyfile(NORMAL_SCAP, TEST_SCAP)
        os.chdir(TEST_EXEC_PATH)
        scappex_.run(TEST_SCAP, silentMode=True)
        self.assertEqual(read_file(TEST_YW7), read_file(NORMAL_YW7))

    def test_scap_to_data(self):
        copyfile(NORMAL_SCAP, TEST_SCAP)
        copyfile(NORMAL_YW7, TEST_YW7)
        os.chdir(TEST_EXEC_PATH)
        scappex_.run(TEST_SCAP, silentMode=True)
        self.assertEqual(read_file(TEST_CHARACTERS_XML), read_file(NORMAL_CHARACTERS_XML))
        self.assertEqual(read_file(TEST_LOCATIONS_XML), read_file(NORMAL_LOCATIONS_XML))
        self.assertEqual(read_file(TEST_ITEMS_XML), read_file(NORMAL_ITEMS_XML))

    def tearDown(self):
        remove_all_testfiles()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
