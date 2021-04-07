from dentmark.defs_manager import DefsManager
from dentmark.parser import Parser

defs_manager = DefsManager()


def parse(file_name_or_str, tag_set_name=None, extra_context = {}, only_address=None):
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
