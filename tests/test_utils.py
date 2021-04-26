from dyc.utils import (
    get_leading_whitespace,
    read_yaml,
    get_indent,
    get_extension,
    is_comment,
)


class TestGetLeadingWhitespace:
    def test_tabs(self):
        """
        Test getting a 'tab' indent from 'get_indent' utility function.

        Parameters
        ----------

        """
        """Test tabs functionality"""
        text = "\t\tHello"
        expected = "\t\t"
        got = get_leading_whitespace(text)
        assert expected == got

    def test_whitespace(self):
        """Test whitespace functionality"""
        space = "                "
        text = "{space}Such a long whitespace".format(space=space)
        expected = space
        got = get_leading_whitespace(text)
        assert expected == got


class TestReadYaml:
    def test_should_return_none_if_not_found(self):
        """
        Test should return 'None' if file does not exist.

        Parameters
        ----------

        """
        random_path = "/path/to/non/existing/file.yaml"
        expected = None
        got = read_yaml(random_path)
        assert expected == got


class TestGetIndent:
    def test_tabs(self):
        """
        Test getting a 'tab' indent from 'get_indent' utility function.

        Parameters
        ----------

        """
        assert get_indent("tab") == "\t"

    def test_2_spaces(self):
        """
        Test getting a 2-space indent from 'get_indent' utility function.

        Parameters
        ----------

        """
        assert get_indent("2 spaces") == "  "

    def test_falsy_value(self):
        """
        Test getting an empty ('falsy') indent from 'get_indent' utility function.

        Parameters
        ----------

        """
        assert get_indent(False) == ""

    def test_default_4_spaces(self):
        """
        Test getting a default indent from 'get_indent' utility function and
        verify it is 4 spaces.

        Parameters
        ----------

        """
        assert get_indent(None) == "    "


class TestGetExtension:
    def test_existing_extension_valid(self):
        """
        Test that 'get_extension' correctly returns filename extension when one exists.

        Parameters
        ----------

        """
        ext = "file.puk"
        expected = "puk"
        got = get_extension(ext)
        assert expected == got

    def test_non_existing_extension(self):
        """
        Test that 'get_extension' returns an empty string when a filename
        lacks an extension.

        Parameters
        ----------

        """
        ext = "file"
        expected = ""
        got = get_extension(ext)
        assert expected == got

    def test_wrong_extension_type(self):
        """
        Test that 'get_extension' returns an empty string when provided invalid
        (non-string) arguments.

        Parameters
        ----------

        """
        exts = [dict(), False, True, [], 123]
        expected = ""
        for ext in exts:
            got = get_extension(ext)
            assert expected == got


class TestIsComment:
    def test_valid_comments(self):
        """Testing valid comments"""
        text = "# Hello World"
        assert is_comment(text, ["#"]) == True

    def test_invalid_comments(self):
        """Testing invalid comments"""
        text = "# Hello World"
        assert is_comment(text, ["//"]) == False
