from dyc.top import TopBuilder
from dyc.utils import get_leading_whitespace, read_yaml, get_indent, get_extension
from dyc.parser import ParsedConfig
import click
import os
import linecache
import tempfile
import unittest


class TestTopFileBuilder(unittest.TestCase):
    def test_is_top_file_documented(self):
        fd, temp_file_name = tempfile.mkstemp()
        os.close(fd)
        f = open(temp_file_name, "w")
        try:
            f.write(config.get("open"))
        finally:
            f.close()
        builder = TopBuilder(temp_file_name, config)
        result = builder.is_top_file_documented()
        self.assertTrue(result)
        os.unlink(temp_file_name)


if __name__ == "__main__":
    unittest.main()
