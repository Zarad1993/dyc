from dyc.top import TopBuilder
from dyc.utils import get_leading_whitespace, read_yaml, get_indent, get_extension
import os
import linecache
import tempfile
import unittest



class TestTopFileBuilder(unittest.TestCase):

    def test_is_top_file_documented(self):
        
        fd, temp_file_name = tempfile.mkstemp()
        config = None
        os.close(fd)
        f = open(temp_file_name, 'w')
        try:
            f.write('"""')
        finally:
            f.close()
        builder = TopBuilder(temp_file_name, config)
        result = builder.is_top_file_documented()
        self.assertTrue(result)
        os.unlink(temp_file_name)

    def test_is_applied(self):
        
        

