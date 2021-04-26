from dyc.classes import (
    ClassBuilder,
    ClassDetails,
    ClassInterface,
    ClassFormatter,
)
from dyc.utils import get_extension
from dyc.dyc import start
import click
from click.testing import CliRunner
import pytest


class TestClassInterface:
    def testSetDocstring(self):
        @click.command()
        def runner():
            interface = ClassInterface(
                "plain", "name", 8, 11, "empty_file", ["x", "y"], {}, 4, False, False
            )
            interface._prompt_docstring()
            print(interface.class_docstring)
            return

        runn = CliRunner()
        # input = ["N", "y", "y", "Class 1 Descritposf"]
        result = runn.invoke(runner, input="test")
        assert result.output.split("\n")[2] == "test"


class TestClassDetails:
    def testExtract(self):
        detail = ClassDetails("(~, y, z)", {})
        detail.extract()
        assert detail.parents == ["~", "y", "z"]

    def testSanitize(self):
        detail = ClassDetails("(~invalid, y, z)", {})
        detail.extract()
        assert detail.parents == ["~invalid", "y", "z"]
        sanitized = list(detail.sanitize())
        assert sanitized == ["y", "z"]

        detail_2 = ClassDetails("(valid, inval!d, also invalid)", {})
        detail_2.extract()
        assert detail_2.parents == ["valid", "inval!d", "also invalid"]
        sanitized = list(detail_2.sanitize())
        assert sanitized == ["valid"]


class TestClassBuilder:
    def testIsClass(self):
        builder = ClassBuilder(
            "filename", {"keywords": ["class"]}, placeholders=False, skip_confirm=False
        )
        assert builder._is_class("class") == True
        assert builder._is_class("classes = 5") == False

    def testGetName(self):
        builder = ClassBuilder(
            "filename", {"keywords": ["class"]}, placeholders=False, skip_confirm=False
        )
        assert builder._get_name("class test") == "test"
        assert builder._get_name("class test()") == "test"
        assert builder._get_name("class test(\n):") == "test"

    def testPrompts(self):
        builder = ClassBuilder(
            "filename", {"keywords": ["class"]}, placeholders=False, skip_confirm=False
        )
        assert builder.details == dict()
        assert builder.prompts() == None

    def testExtractClasses(self):
        builder = ClassBuilder(
            "filename", {"keywords": ["class"]}, placeholders=False, skip_confirm=False
        )
        assert builder.extract_classes("class test(x,y,z)") == ["x", "y", "z"]
        assert builder.extract_classes("class test:") == []

    # IN PROGRESS BELOW
    # CURRENT STATUS: PASSES ON PYTHON 3.8.5, BUT FAILS ON PYTHON 2.7.15

    # @pytest.mark.parametrize("filename", ["tests/test_case_files/class_test_1.py"])
    # def testProcess(self, filename):
    #     # Get oracle file from the filename of the input file
    #     oracle_file = filename.split(".")[0] + "_correct.py"

    #     # Save original contents of test file to a string to rewrite later
    #     with open(filename, "r") as file_obj:
    #         test_file_orig_contents = file_obj.read()

    #     # Save the user input
    #     user_input_file = filename.split(".")[0] + ".in"
    #     with open(user_input_file, "r") as user_input_obj:
    #         user_input = user_input_obj.read()

    #     runner = CliRunner()
    #     result = runner.invoke(start, ["--skip-confirm", filename], input=user_input)

    #     # Compare to Oracle
    #     with open(filename, "r") as file_obj, open(oracle_file, "r") as oracle_obj:
    #         # Replace dumb whitespace
    #         assert file_obj.read().replace(" ", "") == oracle_obj.read().replace(
    #             " ", ""
    #         )

    #     # Write back original contents
    #     with open(filename, "w") as file_obj:
    #         file_obj.write(test_file_orig_contents)
