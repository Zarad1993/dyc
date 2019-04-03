import os
from ..utils import read_yaml

ROOT_PATH = os.getcwd()
DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'defaults.yaml')
CUSTOM = os.path.join(ROOT_PATH, 'dyc.yaml')

class Config(object):

    default = read_yaml(DEFAULT)
    custom = read_yaml(CUSTOM)

    def override(self):
        """
        Entry point to Config, mainly the 
        """
        self._override_basic()
        self._override_formats()

    def _override_basic(self):
        """
        Overrides the current default config's values
        """
        for key, value in self.custom.iteritems():
            if not self._is_mutated(value):
                self.plain[key] = value

    def _override_formats(self):
        """
        Loops over the formats i.e `py`, `js`. And assigns the given customized values
        in Root dyc.yaml file. Otherwise it will use the default values
        """
        formats = self.custom.get('formats', [])
        for index, value in enumerate(formats):
            extension = value.get('extension')
            cnf_index = self._get_custom_extension_index(extension)
            try:
                for nested_key, nested_obj in value.iteritems():
                    try: 
                        self.plain.get('formats')[cnf_index][nested_key].update(**nested_obj) if nested_obj else None
                    except AttributeError:
                        continue
            except (IndexError, TypeError):
                self.plain.get('formats').append(value)

    def _get_custom_extension_index(self, extension):
        """
        If a customised extension is defined. Add that to the config
        """
        for index, value in enumerate(self.plain.get('formats')):
            if value.get('extension') == extension:
                return index

    def _is_mutated(self, value):
        """
        Function that returns weather or not a value can be modified
        """
        return isinstance(value, list) and len(value) and isinstance(value[0], dict)
