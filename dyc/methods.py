import sys
import re
import fileinput
import copy
import linecache
import click
from utils import get_leading_whitespace, BlankFormatter, get_indent, add_start_end
from base import Builder


class MethodBuilder(Builder):
    def __init__(self, filename, config):
        self.filename = filename
        self.config = config

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
        start_line = linecache.getline(filename, start)
        initial_line = line
        start_leading_space = get_leading_whitespace(start_line) # Where function started
        method_string = start_line
        line_within_scope = True
        lineno = start + 1
        line = linecache.getline(filename, lineno)
        end_of_file = False
        end = None
        while (line_within_scope and not end_of_file):
            current_leading_space = get_leading_whitespace(line)
            if len(current_leading_space) <= len(start_leading_space) and line.strip():
                end = lineno - 1
                break
            method_string += line
            lineno = lineno + 1
            line = linecache.getline(filename, int(lineno))
            end_of_file = True if lineno > length else False

        if not end:
            end = length

        return MethodInterface(plain=method_string,
                    name=self._get_name(initial_line),
                    start=start,
                    end=end,
                    filename=filename,
                    arguments=self.extract_arguments(initial_line.strip('\n')),
                    config=self.config,
                    leading_space=get_leading_whitespace(initial_line))

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
        if name not in self.config.get('ignore', []) \
            and not self.is_first_line_documented(result) \
            and click.confirm('Do you want to document method {}?'.format(click.style(name, fg='green'))):
                return True

        return False

    def extract_arguments(self, line):
        """
        Public extract argument method that calls ArgumentDetails
        class to extract args
        Parameters
        ----------
        """
        args = ArgumentDetails(line, self.config.get('arguments', {}))
        args.extract()
        return args.sanitize()

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
        for x in range(result.start, result.end):
            line = linecache.getline(result.filename, x)
            if self.config.get('open') in line:
                returned = True
                break
        return returned

    def prompts(self):
        """
        Abstract prompt method in builder to execute prompts over candidates
        """
        for method_interface in self._method_interface_gen():
            method_interface.prompt() if method_interface else None

    def apply(self):
        """
        Over here we are looping over the result of the
        chosen methods to document and applying the changes to the
        files as confirmed
        """
        for method_interface in self._method_interface_gen():
            if not method_interface:
                continue

            for line in fileinput.input(method_interface.filename, inplace=True):
                if self._get_name(line) == method_interface.name:
                    if self.config.get('within_scope'):
                        sys.stdout.write(line + method_interface.result + '\n')
                    else:
                        sys.stdout.write(method_interface.result + '\n' + line)
                else:
                    sys.stdout.write(line)

    def _method_interface_gen(self):
        """
        A generator that yields the method interfaces
        """
        if not self.details:
            yield None

        for filename, func_pack in self.details.iteritems():
            for method_interface in func_pack.values():
                yield method_interface

    def _get_name(self, line):
        """
        Grabs the name of the method from the given line
        Parameters
        ----------
        str line: String line that has the method's name
        """
        for keyword in self.config.get('keywords', []):
            clear_defs = re.sub('{} '.format(keyword), '', line.strip())
            name = re.sub(r'\([^)]*\)\:', '', clear_defs).strip()
            if re.search(r'\((.*)\)', name):
                name = re.match(r'^[^\(]+', name).group()
            if name:
                return name


class MethodFormatter():

    formatted_string = '{open}{break_after_open}{method_docstring}{break_after_docstring}{argument_format}{break_before_close}{close}'
    fmt = BlankFormatter()

    def format(self):
        """
        Public formatting method that executes a pattern of methods to
        complete the process
        """
        self.pre()
        self.build_docstrings()
        self.build_arguments()
        self.result = self.fmt.format(self.formatted_string, **self.method_format)
        self.add_indentation()
        self.polish()

    def wrap_strings(self, words):
        """
        Compact how many words should be in a line
        Parameters
        ----------
        str words: docstring given
        """
        subs = []
        n = self.config.get('words_per_line')
        for i in range(0, len(words), n):
            subs.append(" ".join(words[i:i+n]))
        return '\n'.join(subs)

    def pre(self):
        """
        In the formatter, this method sets up the object that
        will be used in a formatted way,. Also translates configs
        into consumable values
        """
        method_format = copy.deepcopy(self.config)
        method_format['indent'] = get_indent(method_format['indent']) if method_format['indent'] else '    '
        method_format['indent_content'] = get_indent(method_format['indent']) if get_indent(method_format['indent_content']) else ''
        method_format['break_after_open'] = '\n' if method_format['break_after_open'] else ''
        method_format['break_after_docstring'] = '\n' if method_format['break_after_docstring'] else ''
        method_format['break_before_close'] = '\n' if method_format['break_before_close'] else ''

        argument_format = copy.deepcopy(self.config.get('arguments'))
        argument_format['inline'] = '' if argument_format['inline'] else '\n'

        self.method_format = method_format
        self.argument_format = argument_format

    def build_docstrings(self):
        """
        Mainly adds docstrings of the method after cleaning up text
        into reasonable chunks
        """
        text = self.method_docstring or 'Missing Docstring!'
        self.method_format['method_docstring'] = self.wrap_strings(text.split(' '))

    def build_arguments(self):
        """
        Main function for wrapping up argument docstrings
        """
        if not len(self.arguments):
            self.method_format['argument_format'] = ''
            self.method_format['break_before_close'] = ''
            return

        config = self.config.get('arguments')
        formatted_args = '{prefix} {type} {name}: {doc}'

        title = self.argument_format.get('title')
        if title:
            underline = '-' * len(title)
            self.argument_format['title'] = '{}\n{}\n'.format(title, underline) if config.get('underline') else '{}\n'.format(title)

        result = []

        if len(self.arguments):
            for argument_details in self.arg_docstring:
                argument_details['prefix'] = self.argument_format.get('prefix')
                result.append(self.fmt.format(formatted_args, **argument_details).strip())

        self.argument_format['body'] = '\n'.join(result)
        self.method_format['argument_format'] = self.fmt.format('{title}{body}', **self.argument_format)

    def add_indentation(self):
        """
        Translates indent params to actual indents
        """
        temp = self.result.split('\n')
        space = self.method_format.get('indent')
        indent_content = self.method_format.get('indent_content')
        if indent_content:
            content = temp[1:-1]
            content = [indent_content + docline for docline in temp][1:-1]
            temp[1:-1] = content
        self.result = '\n'.join([space + docline for docline in temp])

    def confirm(self, polished):
        """
        Pop up editor function to finally confirm if the documented
        format is accepted
        Parameters
        ----------
        str polished: complete polished string before popping up
        """
        polished = add_start_end(polished)
        method_split = self.plain.split('\n')
        if self.config.get('within_scope'):
            method_split.insert(1, polished)
        else:
            method_split.insert(0, polished)

        result = '\n'.join(method_split)
        message = click.edit('## CONFIRM: MODIFY DOCSTRING BETWEEN START AND END LINES ONLY\n\n' + result)

        if not message:
            raise QuitConfirmEditor('You quit the editor')

        message = '\n'.join(message.split('\n')[2:])
        final = []
        start = False
        end = False

        for x in message.split('\n'):
            stripped = x.strip()
            if stripped == '## END':
                end = True
            if start and not end:
              final.append(x)
            if stripped == '## START':
                start = True

        self.result = '\n'.join(final)

    def polish(self):
        """
        Editor wrapper to confirm result
        """
        docstring = self.result.split('\n')
        polished = '\n'.join([self.leading_space + docline for docline in docstring])
        self.confirm(polished)


class MethodInterface(MethodFormatter):
    def __init__(self, plain, name, start, end, filename, arguments, config, leading_space):
        self.plain = plain
        self.name = name
        self.start = start
        self.end = end
        self.filename = filename
        self.arguments = arguments
        self.method_docstring = ''
        self.arg_docstring = []
        self.config = config
        self.leading_space = leading_space

    def prompt(self):
        """
        Wrapper method for prompts and calls for prompting args and
        methods then formats them
        """
        self._prompt_docstring()
        self._prompt_args()
        self.format()

    def _prompt_docstring(self):
        """
        Simple prompt for a method's docstring
        """
        echo_name = click.style(self.name, fg='green')
        self.method_docstring = click.prompt('\n({}) Method docstring '.format(echo_name))

    def _prompt_args(self):
        """
        Wrapper for prompting arguments
        """
        def _echo_arg_style(argument):
            """
            Just a small wrapper for echoing args
            Parameters
            ----------
            str argument: argument name
            """
            return click.style('{}'.format(argument), fg='red')
        for arg in self.arguments:
            arg_doc = click.prompt('\n({}) Argument docstring '.format(_echo_arg_style(arg)))
            arg_type = click.prompt('({}) Argument type '.format(_echo_arg_style(arg))) if self.config.get('arguments', {}).get('add_type', False) else ''
            self.arg_docstring.append(dict(type=arg_type, doc=arg_doc, name=arg))


class ArgumentDetails(object):

    def __init__(self, line, config):
        self.line = line
        self.config = config
        self.args = []

    def extract(self):
        """
        Retrieves arguments from a line
        """
        ignore = self.config.get('ignore')
        args = re.search(r'\((.*)\)', self.line).group(1).split(', ')
        self.args = filter(lambda x: x not in ignore, filter(None, [arg.strip() for arg in args]))
        
    def sanitize(self):
        """
        Sanitizes arguments to validate all arguments are correct
        """
        return map(lambda arg: re.findall(r"[a-zA-Z0-9_]+", arg)[0], self.args)
