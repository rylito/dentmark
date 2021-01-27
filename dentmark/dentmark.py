import importlib
import pkgutil
from dentmark.defs_manager import DefsManager
from dentmark.parser import Parser

class Dentmark:
    def __init__(self, defs_module_name=None):
        self.defs_module_name = defs_module_name
        self.available_definitions = self._find_defs()

        if defs_module_name:
            if defs_module_name not in self.available_definitions:
                raise Exception(f'No definitions module named: {defs_module_name}')
            else:
                registered_tags = self.available_definitions[defs_module_name].REGISTERED_TAGS
        else:
            from dentmark.default_definitions import REGISTERED_TAGS
            registered_tags = REGISTERED_TAGS

        self.defs_manager = DefsManager(registered_tags)

    def _find_defs(self):
        return {
            name: importlib.import_module(name)
            for finder, name, ispkg
            in pkgutil.iter_modules()
            if name.startswith('dentmark_')
        }

    def list_defs(self): #TODO for testing, DELME
        print(self.defs_manager.registered_tags)
        print(self.defs_manager.tag_dict)
        print(self.defs_manager.pre_tag_names)

    def render(self, file_name_or_str):
        p = Parser(self.defs_manager, file_name_or_str)
        tree = p.parse()
