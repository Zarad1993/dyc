from dyc.utils import get_leading_whitespace, read_yaml, get_indent, get_extension


class TestGetLeadingWhitespace:
    def test_tabs(self):
        text = '\t\tHello'
        expected = '\t\t'
        got = get_leading_whitespace(text)
        assert expected == got

    def test_whitespace(self):
        space = '                '
        text = '{space}Such a long whitespace'.format(space=space)
        expected = space
        got = get_leading_whitespace(text)
        assert expected == got


class TestReadYaml:
    def test_should_return_none_if_not_found(self):
        random_path = '/path/to/non/existing/file.yaml'
        expected = None
        got = read_yaml(random_path)
        assert expected == got


class TestGetIndent:
    def test_tabs(self):
        assert get_indent('tab') == '\t'

    def test_2_spaces(self):
        assert get_indent('2 spaces') == '  '

    def test_falsy_value(self):
        assert get_indent(False) == ''

    def test_default_4_spaces(self):
        assert get_indent(None) == '    '


class TestGetExtension:
    def test_existing_extension_valid(self):
        ext = 'file.puk'
        expected = 'puk'
        got = get_extension(ext)
        assert expected == got

    def test_non_existing_extension(self):
        ext = 'file'
        expected = ''
        got = get_extension(ext)
        assert expected == got

    def test_wrong_extension_type(self):
        exts = [dict(), False, True, [], 123]
        expected = ''
        for ext in exts:
            got = get_extension(ext)
            assert expected == got
