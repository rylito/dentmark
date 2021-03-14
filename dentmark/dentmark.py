#import importlib
#import pkgutil
from dentmark.defs_manager import DefsManager
from dentmark.parser import Parser

# load the default tags
#import dentmark.default_definitions


#DEFAULT_DEF_SET = 'default'

defs_manager = DefsManager()

#def_tag_set = defs_manager.get_tag_set()

# load the default tags
#import dentmark.default_definitions

#class Dentmark:
    #def __init__(self, defs_module_name=None):
    #def __init__(self):
        #self.defs_module_name = defs_module_name
        #self.available_definitions = self._find_defs()

        #if defs_module_name:
            #if defs_module_name not in self.available_definitions:
                #raise Exception(f'No definitions module named: {defs_module_name}')
            #else:
                #registered_tags = self.available_definitions[defs_module_name].REGISTERED_TAGS
        #else:
            #from dentmark.default_definitions import REGISTERED_TAGS
            #registered_tags = REGISTERED_TAGS


        #self.defs_manager = DefsManager()

        #if registered_tags is None:
            #from dentmark.default_definitions import REGISTERED_TAGS
            #registered_tags = REGISTERED_TAGS


    #def _find_defs(self):
        #return {
            #name: importlib.import_module(name)
            #for finder, name, ispkg
            #in pkgutil.iter_modules()
            #if name.startswith('dentmark_')
        #}


def parse(file_name_or_str, tag_set_name=None, extra_context = {}, only_address=None):
    #if tag_set_name is None or tag_set_name == DEFAULT_DEF_SET:
        #if def_tag_set.empty:
            # load the default tags
            #import dentmark.default_definitions
        #use_tag_set = def_tag_set
    use_tag_set = defs_manager.get_tag_set(tag_set_name)

    p = Parser(use_tag_set, file_name_or_str, extra_context)
    return p.parse(only_address)


def render(file_name_or_str, tag_set_name=None, extra_context={}):
    root = parse(file_name_or_str, tag_set_name, extra_context)
    root.pre_render()
    rendered = root.render()
    return rendered


def add_element(file_name_or_str, tag_id, new_tag_name, value):
    root = parse(file_name_or_str)
    found_element = root.get_tag_by_id(tag_id)
    if found_element is None:
        raise Exception('Element for tag_id not found: {tag_id}')
    found_element.add_child_element(defs_manager, new_tag_name, value)
    return root
