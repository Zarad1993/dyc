"""
Reusable methods throughout DYC
"""
import os
import yaml
import string

INDENT_OPTIONS = {"tab": "\t", "2 spaces": "  ", "False": ""}


def get_leading_whitespace(s):
    """
    Gets the leading whitespace of a string. Mainly used to
    determine how many space were there originally before adding a
    docstring. So that a docstring is placed in the same
    pattern
    Parameters
    ----------
    str s: String text
    """
    accumulator = []
    for c in s:
        if c in " \t\v\f\r\n":
            accumulator.append(c)
        else:
            break
    return "".join(accumulator)


def read_yaml(path):
    """
    Yaml Reader method
    Parameters
    ----------
    str path: path of file
    """
    try:
        with open(path, "r") as config:
            try:
                return yaml.safe_load(config)
            except yaml.YAMLError as exc:
                return None
    except IOError as io_err:
        return None


class BlankFormatter(string.Formatter):
    def __init__(self, default=""):
        self.default = default

    def get_value(self, key, args, kwds):
        """"""
        if isinstance(key, str):
            return kwds.get(key, self.default)
        else:
            return string.Formatter.get_value(key, args, kwds)


def get_indent(space):
    """
    Translator of the indent config param to real spaces or
    tabs
    Parameters
    ----------
    str space: The value of `indent` in a config file
    """
    value = INDENT_OPTIONS.get(str(space))
    if value is None:
        return "    "
    return value


def get_extension(filename):
    """
    Gets the extension of a file
    Parameters
    ----------
    str filename: the filename to extract extension from
    """
    try:
        return os.path.splitext(filename)[1].replace(".", "")
    except (AttributeError, TypeError):
        return ""


def all_files_generator(extensions=[]):
    """
    A generator that yields all candidate files to add docstrings
    on
    Parameters
    ----------
    list extensions: Allowed extensions on a file
    """
    for root, dirs, files in os.walk(os.getcwd()):
        files = [os.path.join(root, f) for f in files if not f[0] == "."]
        dirs[:] = [d for d in dirs if not d[0] == "."]
        if extensions:
            files = [
                filename for filename in files if get_extension(filename) in extensions
            ]
        yield files


def add_start_end(string):
    """
    Utility method add the START and END for a docstring
    so that it could be presented in an editor for the user to know what
    can be edited
    Parameters
    ----------
    str string: large text
    """
    leading_space = get_leading_whitespace(string)
    start = "{}## START\n".format(leading_space)
    end = "\n{}## END".format(leading_space)
    string.split("\n")
    result = start + string + end
    return result


def get_file_lines(name):
    """
    Get the number of lines in a file
    Parameters
    ----------
    str name: filepath and name of file
    """
    lines = 0
    with open(name, "r") as stream:
        lines = len(stream.readlines())
    return lines


def get_hunk(patch):
    """
    Gets the hunk of a patch from the diff pattern
    Parameters
    ----------
    str patch: Diff patched text
    """
    import re

    pat = r".*?\@\@(.*)\@\@.*"
    match = re.findall(pat, patch)
    return [m.strip() for m in match]


def get_additions_in_first_hunk(hunk):
    """
    Pulls the additions from a hunk of a diff patch
    Parameters
    ----------
    str hunk: Git diff Hunk
    """
    if not isinstance(hunk, list):
        return None, None
    if len(hunk) < 1:
        return None, None
    adds_patch = hunk[0].split("+")[-1].split(",")
    start = int(adds_patch[0])
    end = int(start) + int(adds_patch[1])
    return start, end


def is_one_line_method(line, keywords):
    """
    Gets True if the line holds a complete method declaration (from 'def to :), 
    otherwise it gets False
    ----------
    str line: Text line
    list keywords: list of keywords like def for python, func for go etc.
    """
    found = [word.lstrip() for word in line.split(" ") if word.lstrip() in keywords]
    if found:
        return line.count("(") == line.count(")")
    return bool(found)


def is_comment(line, comments):
    """
    A utility method to tell if the provided line is
    a comment or not

    Parameters
    ----------
    str line: The line string in a file
    list comments: A list of potential comment keywords
    """
    return line.lstrip(' ')[0] in comments
