from dyc.classes import (
    ClassBuilder,
    ClassDetails,
    ClassInterface,
    ClassFormatter,
)
import click
from click.testing import CliRunner


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
