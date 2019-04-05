import fileinput
from utils import all_files_generator, get_file_lines


class Builder(object):
    details = dict()

    def initialize(self, change=None):
        """
        The Builder's main method. It stores all the changes that needs to be made
        in `self.details` for a file. Which would then be used to add Docstrings to.
        """
        result = dict()

        patches = []
        if change:
            patches = change.get('additions')

        for line in fileinput.input(self.filename):
            filename = fileinput.filename()
            lineno = fileinput.lineno()
            keywords = self.config.get('keywords')
            found = len(filter(lambda word: word.lstrip() in keywords, line.split(' '))) > 0

            if change and found:
                found = self._is_line_part_of_patches(lineno, line, patches)

            if not self.details.get(filename):
                self.details[filename] = dict()

            if found:
                length = get_file_lines(filename)
                result = self.extract_and_set_information(filename, lineno, line, length)
                if self.validate(result):
                    self.details[filename][result.name] = result

    def _is_line_part_of_patches(self, lineno, line, patches):
        """
        Checks if a line is part of the patch
        Parameters
        ----------
        int lineno: Line number
        str line: Line text in a patch
        list patches: List of patches
        """
        result = False
        for change in patches:
            start, end = change.get('hunk')
            if start <= lineno <= end:
                patch = change.get('patch')
                found = filter(lambda l: line.replace('\n', '') == l, patch.split('\n'))
                if found:
                    result = True
                    break
        return result

    def clear(self, filename):
        """
        Clear changes in a filename
        """
        try:
            del self.details[filename]
        except KeyError:
            # Probably the filename is not already there
            return

    def prompts(self):
        """
        Abstract method to get inputs from user
        """
        pass

    def apply(self):
        """
        Abstract method to changes on the file
        """
        pass


class FilesDirector():

    WILD_CARD = ['.', '*']

    def prepare_files(self, files=[]):
        """
        Main method to prepare files to read, goes along excludes
        and includes
        Parameters
        ----------
        list files: list of pre-given files
        """
        self.set_files_to_read(files=files)
        self.apply_includes()
        self.apply_excludes()

    def apply_includes(self):
        """
        TODO function that applies includes config
        """
        pass

    def apply_excludes(self):
        """
        TODO Method for removing files from a file list
        """
        pass

    def set_files_to_read(self, files=[]):
        """
        Sets files that we will loop over in file_list property
        Parameters
        ----------
        list files: Pre-given files list
        """
        if self.config.get('file_list'):
            # File list has already been passed
            self.file_list = self.config.get('file_list')
            return

        if len(files):
            self.file_list = files
            return

        result = []
        for paths in all_files_generator(extensions=self.extensions):
            result += paths

        self.file_list = result


class FormatsDirector():

    formats = dict()

    def prepare_formats(self):
        """
        Function that prepares allowed formats
        """
        self.formats = {ext.get('extension'): ext for ext in self.config.get('formats')}


class Processor(FilesDirector, FormatsDirector):
    """Subclass process that runs complete lifecycle for DYC"""
    def start(self):
        """
        TODO Method wrapper for starting the process
        """
        pass
        # self.setup()
        # self.prompts()
        # self.apply()

    def prepare(self, files=[]):
        """
        Public method that sets up part of the configuration
        Parameters
        ----------
        list files: list of given files shall they are predefined in a custom configuration or a passed diff
        """
        self.prepare_files(files=files)
        self.prepare_formats()

    @property
    def extensions(self):
        """
        Property that returns all the allowed extensions
        """
        return filter(None, map(lambda fmt: fmt.get('extension'), self.config.get('formats')))
