from dentmark.tag_def import TagDef, Optional, OptionalUnique, Required, RequiredUnique

from dentmark.dentmark import defs_manager
def_tag_set = defs_manager.get_tag_set()



class List(TagDef):

    min_num_text_nodes = 0
    max_num_text_nodes = 0

    def render_main(self):
        return f'<{self.tag_name}>{self.content}</{self.tag_name}>'

@def_tag_set.register()
class ListItem(TagDef):
    tag_name = 'li'

    # allow nesting li 4 levels deep
    parents = [Optional('root.ul'), Optional('root.ol'), Optional('root.ul.li'), Optional('root.ul.li.li'), Optional('root.ul.li.li.li'),Optional('root.ol.li'), Optional('root.ol.li.li'), Optional('root.ol.li.li.li'), Optional('root.ol.li.ul'), Optional('root.ul.li.ol')]

    def render_main(self):
        return f'<li>{self.content}</li>'

    def before_render(self):
        # wrap any adjacent child li in the same type of list as outer list (ul or ol). Makes it easier to create sub-lists

        parent = self.parent
        while parent.tag_name == 'li':
            parent = parent.parent

        new_children = []
        list_wrapper_elem = None

        for child in self.children:
            if child.is_element and child.tag_name == 'li':
                if list_wrapper_elem is None:
                    list_wrapper_def = def_tag_set.get_def(parent.address)
                    # TODO Just use None for num_of_type etc. here... Might be better way to handle appending elements after render
                    list_wrapper_elem = list_wrapper_def(parent.tag_name, f'{self.address}.{parent.tag_name}', None, child.indent_level, self, self.root, None, None, False, False, {})
                    new_children.append(list_wrapper_elem)
                list_wrapper_elem.children.append(child)
            else:
                list_wrapper_elem = None
                new_children.append(child)
        self.children = new_children


@def_tag_set.register()
class UnorderedList(List):
    tag_name = 'ul'

    parents = [Optional('root'), Optional('root.ol.li')]

@def_tag_set.register()
class OrderedList(List):
    tag_name = 'ol'

    parents = [Optional('root'), Optional('root.ul.li')]
