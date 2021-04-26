import sys
import fileinput
import linecache
import click
import os
import re
import copy
from .utils import (
    get_leading_whitespace,
    add_start_end,
    is_comment,
    is_one_line_method,
    BlankFormatter,
    get_indent,
)
from .base import Builder


class ClassBuilder(Builder):
    already_printed_filepaths = []  # list of already printed files

    def validate(self, result):
        """
        An abstract validator method that checks if the class is
        still valid and gives the final decision
        Parameters
        ----------
        ClassInterface result: The Class Interface result
        """
        if not result:
            return False
        name = result.name
        if name not in self.config.get(
            "ignore", []
        ) and not self.is_first_line_documented(result):
            if (
                self.filename not in self.already_printed_filepaths
            ):  # Print file of class to document
                click.echo(
                    "\n\nIn file {} :\n".format(
                        click.style(
                            os.path.join(*self.filename.split(os.sep)[-3:]), fg="red"
                        )
                    )
                )
                self.already_printed_filepaths.append(self.filename)
            confirmed = (
                True
                if self.placeholders
                else click.confirm(
                    "Do you want to document class {}?".format(
                        click.style(name, fg="green")
                    )
                )
            )
            if confirmed:
                return True

        return False

    def is_first_line_documented(self, result):
        """
        A boolean function that determines weather the first line has
        a docstring or not
        Parameters
        ----------
        ClassInterface result: Is a class interface class that could be
        subject to be taking a docstring
        str line: The line of the found class
        """
        returned = False
        # copied from pull request related to issue #63
        read_first_line = linecache.getline(result.filename, result.start)
        read_second_line = linecache.getline(result.filename, result.start + 1)
        finalTwoLines = read_first_line + "\n" + read_second_line
        # The open_brace_pattern is """ by default, but can be configured in the yml files
        open_brace_pattern = self.config.get("open", None)
        pattern = r":\n\s*?({})".format(open_brace_pattern)
        # Other experimental regexe patterns below
        #:\n\s{4}(?:""")   #r':[\s\S]?[\n][\s]*(""")'
        match = re.search(pattern, finalTwoLines)
        returned = True if match else False

        linecache.clearcache()
        return returned

    def extract_and_set_information(self, filename, start, line, length):
        """
        This is a main abstract method tin the builder base
        to add result into details. Used in Class Builder to
        pull the candidates that are subject to docstrings
        Parameters
        ----------
        str filename: The file's name
        int start: Starting line
        str line: Full line text
        int length: The length of the extracted data
        """
        # ------------------------------#
        # CAN GENERALIZE THIS FUNCTION #
        # ------------------------------#
        start_line = linecache.getline(filename, start)
        initial_line = line
        start_leading_space = get_leading_whitespace(
            start_line
        )  # Where function started
        class_string = start_line
        if not is_one_line_method(start_line, self.config.get("keywords")):
            class_string = line
            linesBackwards = class_string.count("\n") - 1
            start_leading_space = get_leading_whitespace(
                linecache.getline(filename, start - linesBackwards)
            )
        line_within_scope = True
        lineno = start + 1
        line = linecache.getline(filename, lineno)
        end_of_file = False
        end = None
        while line_within_scope and not end_of_file:
            current_leading_space = get_leading_whitespace(line)
            if len(current_leading_space) <= len(start_leading_space) and line.strip():
                end = lineno - 1
                break
            class_string += line
            lineno = lineno + 1
            line = linecache.getline(filename, int(lineno))
            end_of_file = True if lineno > length else False

        if not end:
            end = length

        linecache.clearcache()
        return ClassInterface(
            plain=class_string,
            name=self._get_name(initial_line),
            start=start,
            end=end,
            filename=filename,
            classes=self.extract_classes(initial_line.strip("\n")),
            config=self.config,
            leading_space=get_leading_whitespace(initial_line),
            placeholders=self.placeholders,
            skip_confirm=self.skip_confirm,
        )

    def extract_classes(self, line):
        """
        Public method to extract parents that calls ClassDetails
        class to extract parents
        Parameters
        ----------
        str line: line that contains the parents of the class
        """
        parents = ClassDetails(line, self.config.get("parents", {}))
        parents.extract()
        return parents.sanitize()

    def prompts(self):
        """
        Abstract prompt method in builder to execute prompts over candidates
        """
        for class_interface in self._class_interface_gen():
            class_interface.prompt() if class_interface else None

    def _class_interface_gen(self):
        """
        A generator that yields the class interfaces
        """
        if not self.details:
            yield None
        for filename, func_pack in self.details.items():
            for class_interface in func_pack.values():
                yield class_interface

    def apply(self):
        """
        Over here we are looping over the result of the
        chosen classes to document and applying the changes to the
        files as confirmed
        """
        for class_interface in self._class_interface_gen():
            if not class_interface:
                continue
            fileInput = fileinput.input(class_interface.filename, inplace=True)

            for line in fileInput:
                tmpLine = line
                if self._is_class(line) and ":" not in line:
                    openedP = line.count("(")
                    closedP = line.count(")")
                    pos = 1
                    if openedP == closedP:
                        continue
                    else:
                        while openedP != closedP:
                            tmpLine += fileInput.readline()
                            openedP = tmpLine.count("(")
                            closedP = tmpLine.count(")")
                            pos += 1
                        line = tmpLine

                if self._get_name(line) == class_interface.name:
                    if self.config.get("within_scope"):
                        sys.stdout.write(line + class_interface.result + "\n")
                    else:
                        sys.stdout.write(class_interface.result + "\n" + line)
                else:
                    sys.stdout.write(line)

    def _get_name(self, line):
        """
        Grabs the name of the class from the given line
        Parameters
        ----------
        str line: String line that has the class' name
        """
        for keyword in self.config.get("keywords", []):
            clear_defs = re.sub("{} ".format(keyword), "", line.strip())
            name = re.sub(r"\([^)]*\)\:", "", clear_defs).strip()
            if re.search(r"\(([\s\S]*)\)", name):
                try:
                    name = re.match(r"^[^\(]+", name).group()
                except:
                    pass
            if name:
                return name

    def _is_class(self, line):
        """
        A predicate method that checks if a line is a
        class

        Parameters
        ----------
        str line: Text string of a line in a file
        """
        return line.strip().split(" ")[0] in self.config.get("keywords")


class ClassFormatter:

    formatted_string = "{open}{break_after_open}{class_docstring}{break_after_docstring}{empty_line}{parents_format}{break_before_close}{close}"
    fmt = BlankFormatter()

    def format(self, skip_confirm):
        """
        Public formatting method that executes a pattern of methods to
        complete the process
        """
        self.pre()
        self.build_docstrings()
        self.build_parents()
        self.result = self.fmt.format(self.formatted_string, **self.class_format)
        self.add_indentation()
        self.polish()
        self.skip_confirm = skip_confirm

    def wrap_strings(self, words):
        """
        Compact how many words should be in a line
        Parameters
        ----------
        str words: docstring given
        """
        subs = []
        n = self.config.get("words_per_line")
        for i in range(0, len(words), n):
            subs.append(" ".join(words[i : i + n]))
        return "\n".join(subs)

    def pre(self):
        """
        In the formatter, this method sets up the object that
        will be used in a formatted way,. Also translates configs
        into consumable values
        """
        class_format = copy.deepcopy(self.config)
        class_format["indent"] = (
            get_indent(class_format["indent"]) if class_format["indent"] else "    "
        )
        class_format["indent_content"] = (
            get_indent(class_format["indent"])
            if get_indent(class_format["indent_content"])
            else ""
        )
        class_format["break_after_open"] = (
            "\n" if class_format["break_after_open"] else ""
        )
        class_format["break_after_docstring"] = (
            "\n" if class_format["break_after_docstring"] else ""
        )
        class_format["break_before_close"] = (
            "\n" if class_format["break_before_close"] else ""
        )
        class_format["empty_line"] = "\n"

        parents_format = copy.deepcopy(self.config.get("parents"))
        parents_format["inline"] = "" if parents_format["inline"] else "\n"

        self.class_format = class_format
        self.parents_format = parents_format

    def build_docstrings(self):
        """
        Mainly adds docstrings of the class after cleaning up text
        into reasonable chunks
        """
        text = self.class_docstring or "Missing Docstring!"
        self.class_format["class_docstring"] = self.wrap_strings(text.split(" "))

    def build_parents(self):
        """
        Main function for wrapping up parent docstrings
        """
        if not self.classes:  # if len(self.classes) == 0
            self.class_format["parents_format"] = ""
            self.class_format["break_before_close"] = ""
            self.class_format["empty_line"] = ""
            return

        config = self.config.get("parents")
        formatted_parents = "{prefix} {name}: {doc}"

        title = self.parents_format.get("title")
        if title:
            underline = "-" * len(title)
            self.parents_format["title"] = (
                "{}\n{}\n".format(title, underline)
                if config.get("underline")
                else "{}\n".format(title)
            )

        result = []

        if self.classes:  # if len(self.classes) > 0
            for parent_details in self.class_parent_list:
                parent_details["prefix"] = self.parents_format.get("prefix")

                result.append(
                    self.fmt.format(formatted_parents, **parent_details).strip()
                )

        self.parents_format["body"] = "\n".join(result)
        self.class_format["parents_format"] = self.fmt.format(
            "{title}{body}", **self.parents_format
        )

    def add_indentation(self):
        """
        Translates indent params to actual indents
        """
        temp = self.result.split("\n")
        space = self.class_format.get("indent")
        indent_content = self.class_format.get("indent_content")
        if indent_content:
            content = temp[1:-1]
            content = [indent_content + docline for docline in temp][1:-1]
            temp[1:-1] = content
        self.result = "\n".join([space + docline for docline in temp])

    def confirm(self, polished):
        """
        Pop up editor function to finally confirm if the documented
        format is accepted
        Parameters
        ----------
        str polished: complete polished string before popping up
        """
        polished = add_start_end(polished)
        class_split = self.plain.split("\n")
        if self.config.get("within_scope"):
            # Check if class comes in an unusual format
            keywords = self.config.get("keywords")
            firstLine = class_split[0]
            pos = 1
            while not is_one_line_method(firstLine, keywords):
                firstLine += class_split[pos]
                pos += 1
            class_split.insert(pos, polished)
        else:
            class_split.insert(0, polished)

        try:
            result = "\n".join(class_split)

            # If running an automated test, skip the editor confirmation
            if self.skip_confirm:
                message = result
            else:
                message = click.edit(
                    "## CONFIRM: MODIFY DOCSTRING BETWEEN START AND END LINES ONLY\n\n"
                    + result
                )
                message = (
                    result if message == None else "\n".join(message.split("\n")[2:])
                )
        except:
            print("Quitting the program in the editor terminates the process. Thanks")
            sys.exit()

        final = []
        start = False
        end = False

        for x in message.split("\n"):
            stripped = x.strip()
            if stripped == "## END":
                end = True
            if start and not end:
                final.append(x)
            if stripped == "## START":
                start = True

        self.result = "\n".join(final)

    def polish(self):
        """
        Editor wrapper to confirm result
        """
        docstring = self.result.split("\n")
        polished = "\n".join([self.leading_space + docline for docline in docstring])
        if self.placeholders:
            self.result = polished
        else:
            self.confirm(polished)


class ClassInterface(ClassFormatter):
    def __init__(
        self,
        plain,
        name,
        start,
        end,
        filename,
        classes,
        config,
        leading_space,
        placeholders,
        skip_confirm,
    ):
        self.plain = plain
        self.name = name
        self.start = start
        self.end = end
        self.filename = filename
        self.classes = classes
        self.class_docstring = ""
        self.class_parent_list = []
        self.config = config
        self.leading_space = leading_space
        self.placeholders = placeholders
        self.skip_confirm = skip_confirm

    def prompt(self):
        self._prompt_docstring()
        self._prompt_parents()
        self.format(skip_confirm=self.skip_confirm)

    def _prompt_docstring(self):
        """
        Simple prompt for a class' docstring
        """
        if self.placeholders:
            self.class_docstring = "<docstring>"
        else:
            echo_name = click.style(self.name, fg="green")
            self.class_docstring = click.prompt(
                "\n({}) Class docstring ".format(echo_name)
            )

    def _prompt_parents(self):
        """
        Wrapper for classes
        """

        def _echo_parent_style(parent):
            """
            Just a small wrapper for echoing parentss
            Parameters
            -----------
            str parent: parent name
            """
            return click.style("{}".format(parent), fg="red")

        for parent in self.classes:
            doc_placeholder = "<parent docstring>"
            parent_doc = (
                click.prompt(
                    "\n({}) Inherited class docstring ".format(
                        _echo_parent_style(parent)
                    )
                )
                if not self.placeholders
                else doc_placeholder
            )
            self.class_parent_list.append(dict(doc=parent_doc, name=parent))


class ClassDetails(object):
    def __init__(self, line, config):
        self.line = line
        self.config = config
        self.parents = []

    def extract(self):
        """
        Retrieves class parents from a line and cleans them
        """
        try:
            parents = re.search(r"\(([\s\S]*)\)", self.line).group(1).split(",")
            self.parents = [
                parent.replace("\n", "").replace("\t", "").strip() for parent in parents
            ]
        except:
            pass
        self.parents = [parent for parent in self.parents if parent != ""]

    def sanitize(self):
        """
        Sanitizes classes to validate all classes are correct
        """
        # Updated filter function to remove invalid parent names due to bad syntax
        return list(
            filter(
                lambda parent: not re.findall(r"[^a-zA-Z0-9_]", parent), self.parents
            )
        )
