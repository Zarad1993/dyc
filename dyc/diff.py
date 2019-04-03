"""
Ideally, this file is to get the current staged
in Git Diff, then creates a `.dyc.patch` temporary file.

The file will patch will undergo the process of:
1 - See where the `Added` lines fall in
2 - Extract methods that fall within the added lines and dump them into `.dyc.patch`
"""
import os
import git
import ntpath
import linecache
from utils import get_hunk, get_additions_in_first_hunk
from base import Processor

class DiffParser():

    PREFIX = 'diff --git'

    def parse(self, staged=False):
        """
        Main parser method that gets all the mandatory information from
        a Diff chunk
        Parameters
        ----------
        bool staged: Only using the staged files
        """
        self.diffs = self.repo.index.diff('HEAD' if staged else None)
        self.plain = self.repo.git.diff('HEAD').split('\n')
        return self._pack()

    def _pack(self):
        """
        Wrapper that packs the information that'll be parsed
        """
        patches = []
        for diff in self.diffs:
            if not self.is_candidate(diff.a_path):
                print('File {} is not a candidate to apply DYC'.format(diff.a_path))
                continue
            sep = '{} a/{} b/{}'.format(self.PREFIX, diff.a_path, diff.b_path)
            patch = self.__clean(self.__patch(sep), diff)
            patches.append(patch)
        return patches

    def is_candidate(self, path):
        """
        Check if a file is a candidate to being documented
        after looking at the allowed files from file_list
        Parameters
        ----------
        str path: path of a file
        """
        full_path = os.path.join(os.getcwd(), path)
        return full_path in self.file_list

    def __patch(self, separator):
        """
        A method that returns a patch
        Parameters
        ----------
        str separator: Main separators from a diff chunk
        """
        patch = []
        hit = False
        # end = False
        for line in self.plain:
            if line == separator:
                hit = True
                continue
            elif line.startswith(self.PREFIX) and hit:
                break
            elif hit:
                patch.append(line)
        return '\n'.join(patch)

    def __pack(self, patch):
        """
        Packer to get from the chunk of diffs and attach
        to additions
        Parameters
        ----------
        str patch: Patched diff text
        """
        final = []
        result = []
        hit = False
        start, end = None, None
        for index, line in enumerate(patch):
            _hunk = get_hunk(line)

            if (len(patch) -1) == index:
                final.append(dict(patch='\n'.join(result), hunk=(start, end)))

            if len(_hunk) and not hit:
                start, end = get_additions_in_first_hunk(get_hunk(line))
                hit = True
                continue
            elif len(_hunk) and hit:
                final.append(dict(patch='\n'.join(result), hunk=(start, end)))
                start, end = get_additions_in_first_hunk(get_hunk(line))
                result = []
                hit = True
            elif hit:
                result.append(line)

        return final


    def __clean(self, patch, diff):
        """Returns a clean dict of a path"""
        result = {}
        result['additions'] = self.__additions(self.__pack(patch.split('\n')), diff.a_path) # [{hunk: (start, end), patch:}]
        result['plain'] = patch
        result['diff'] = diff
        result['name'] = ntpath.basename(diff.a_path)
        result['path'] = diff.a_path
        return result

    def __additions(self, hunks, path):
        """
        Function that returns only the added text in a file
        Parameters
        ----------
        list hunks: Group of added texts
        str path: path of a file
        """
        for hunk in hunks:
            patch = hunk.get('patch')
            result = []
            for line in patch.split('\n'):
                try:
                    if line[0] == '+' and not line.startswith('+++'):
                        l = line[1:]
                        result.append(l)
                except IndexError as e:
                    print(e.message)
                    continue
            hunk['patch'] = '\n'.join(result)
        return hunks


class Diff(DiffParser, Processor):
    def __init__(self, config):
        self.repo = git.Repo(os.getcwd())
        self.config = config
        self.prepare()

    @property
    def uncommitted(self):
        """
        Property method that returns all uncommitted information
        """
        return self._uncommitted()

    def _uncommitted(self):
        """
        Private method to return the data for the publich uncommitted
        property
        """
        return self.parse()
