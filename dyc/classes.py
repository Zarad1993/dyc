import sys
import fileinput
import linecache
import click
import os
import re
from .utils import get_leading_whitespace, add_start_end, is_comment, is_one_line_method
from .base import Builder
from .methods import ArgumentDetails


class ClassBuilder(Builder):
    already_printed_filepaths = []  # list of already printed files

    def validate(self, result):
        """
        An abstract validator method that checks if the method is
        still valid and gives the final decision
        Parameters
        ----------
        MethodInterface result: The Method Interface result
        """
        if not result:
            return False
        name = result.name
        if name not in self.config.get(
            "ignore", []
        ) and not self.is_first_line_documented(result):
            if (
                self.filename not in self.already_printed_filepaths
            ):  # Print file of method to document
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
        MethodInterface result: Is a method interface class that could be
        subject to be taking a docstring
        str line: The line of the found method
        """
        returned = False
        # print(result.start, ' ', result.end)
        # for x in range(result.start, result.end):
        #     line = linecache.getline(result.filename, x)
        #     if self.config.get("open") in line:
        #         returned = True
        #         break

        # copied from pull request
        read_first_line=linecache.getline(result.filename, result.start)
        read_second_line=linecache.getline(result.filename, result.start+1)
        finalTwoLines=read_first_line+"\n"+read_second_line
        # 1. Changed long regex since the assumption is that the line already has the keyword (e.g. def, class) in it
        # 2. Can use a simpler regex
        # 3. Potentially replace """ with config[class][open] as value
        pattern = r':[\s\S]?[\n][\s]*(""")'
        match = re.search(pattern,finalTwoLines)
        returned = True if match else False

        linecache.clearcache()
        return returned

    def extract_and_set_information(self, filename, start, line, length):
        """
        This is a main abstract method tin the builder base
        to add result into details. Used in Method Builder to
        pull the candidates that are subject to docstrings
        Parameters
        ----------
        str filename: The file's name
        int start: Starting line
        str line: Full line text
        int length: The length of the extracted data
        """
        #------------------------------#
        # CAN GENERALIZE THIS FUNCTION #
        #------------------------------#
        start_line = linecache.getline(filename, start)
        initial_line = line
        start_leading_space = get_leading_whitespace(
            start_line
        )  # Where function started
        class_string = start_line
        if not is_one_line_method(start_line, self.config.get("keywords")):
            class_string = line
            linesBackwards = class_string.count("\n")  - 1
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
            end = end,
            filename = filename,
            arguments = self.extract_arguments(initial_line.strip("\n")),
            config = self.config,
            leading_space=get_leading_whitespace(initial_line),
            placeholders=self.placeholders
        )

    def extract_arguments(self, line):
        """
        Public extract argument method that calls ArgumentDetails
        class to extract args
        Parameters
        ----------
        """
        args = ArgumentDetails(line, self.config.get("arguments", {}))
        args.extract()
        return args.sanitize()
    
    def prompts(self):
        """
        Abstract prompt method in builder to execute prompts over candidates
        """
        # Do a prompt for each class interface
        print("SELF.DETAILS: ", self.details)

        for class_interface in self._class_interface_gen():
            class_interface.prompt() if class_interface else None
    

    def _class_interface_gen(self):
        # For each ClassInterface object in details[filename][class_name]
        pass

    def apply(self):
        # For each ClassInterface object (_class_interface_gen again for this)
        # Essentially the same as methodbuilder's apply
        pass

    def _get_name(self, line):
        """
        Grabs the name of the method from the given line
        Parameters
        ----------
        str line: String line that has the method's name
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

    # Dumb duplicate of _is_class
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

    def format(self):
        # Gonna have to look at how MethodFormatter does it
        # Basically the same as that, tho, as the docstrings should be formatted the same
        pass


class ClassInterface(ClassFormatter):
    def __init__(
        self,
        plain,
        name,
        start,
        end,
        filename,
        arguments,
        config,
        leading_space,
        placeholders,
    ):
        self.plain = plain
        self.name = name
        self.start = start
        self.end = end
        self.filename = filename
        self.arguments = arguments
        self.class_docstring = ""
        self.arg_docstring = []
        self.config = config
        self.leading_space = leading_space
        self.placeholders = placeholders

    def prompt(self):
        # Wrapper method for prompting user related to the Class
        self._prompt_docstring()
        self._prompt_args()
        self.format()
    
    def _prompt_docstring(self):
        # Prompt user for main docstring title of class
        pass
    
    def _prompt_args(self):
        # Prompting for arguements (look at MethodInterface class)
        pass


