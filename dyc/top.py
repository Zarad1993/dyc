import sys
import fileinput
import linecache
import click
from .utils import get_leading_whitespace, add_start_end
from .base import Builder


class TopBuilder(Builder):
    is_validated = False

    def validate(self):
        """
        An abstract validator method that checks if the top is
        still valid and gives the final decision
        """
        current_file_dir = self.filename.split("\\")
        if not self.is_top_file_documented():
            confirmed = click.confirm(
                "Do you want to document top of file {}?".format(
                    click.style("\\".join(current_file_dir[-3:]), fg="green")
                )
            )
            if confirmed:
                return True

        return False

    def is_top_file_documented(self):
        """
        A boolean function that determines weather the first line has
        a docstring or not
        """
        returned = False
        line = linecache.getline(self.filename, 1)
        if self.config.get("open") in line:
            returned = True
        linecache.clearcache()
        return returned

    def prompts(self):
        self._prompt_docstring()
        # TODO: Prompt args here as well

    def _prompt_docstring(self):

        self.Top_docstring = ""
        if self.validate():
            self.is_validated = True
            if self.placeholders:
                self.Top_docstring = "<docstring>"
            else:
                name = click.style(self.filename, fg="green")
                self.Top_docstring = click.prompt("\n({}) Top docstring ".format(name))

    def apply(self):
        if self.is_validated:
            self.polish()
            final_result = self.wrap_doc_strings(self.result)

            for i, line in enumerate(fileinput.input(self.filename, inplace=True)):
                if i == 0:
                    sys.stdout.write(final_result + "\n" + line)
                else:
                    sys.stdout.write(line)

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

    def confirm(self, polished):
        result = add_start_end(polished)
        preview_line1, preview_line2 = (
            linecache.getline(self.filename, 1),
            linecache.getline(self.filename, 2),
        )
        linecache.clearcache()
        try:
            message = click.edit(
                "## CONFIRM: MODIFY DOCSTRING BETWEEN START AND END LINES ONLY\n\n"
                + result
                + "\n"
                + preview_line1
                + preview_line2
            )
            message = "\n".join(message.split("\n")[2:])
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
        docstring = self.Top_docstring.split("\n")
        polished = "\n".join([docline for docline in docstring])
        if self.placeholders:
            self.result = polished
        else:
            self.confirm(polished)

    def wrap_doc_strings(self, s):
        leading_space = get_leading_whitespace(s)
        start = '{}"""\n'.format(leading_space)
        end = '\n{}"""'.format(leading_space)
        s.split("\n")
        result = start + s + end
        return result
