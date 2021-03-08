from dentmark.tag_def import TagDef, Optional, OptionalUnique, Required, RequiredUnique

from dentmark.dentmark import defs_manager
def_tag_set = defs_manager.get_tag_set()



#@def_tag_set.register()
class List(TagDef):
    #allow_children = ['li']

    parents = [Optional('root')]

    def render_main(self):
        return f'<{self.tag_name}>{self.content}</{self.tag_name}>'

@def_tag_set.register()
class ListItem(TagDef):
    tag_name = 'li'
    #exclude_children = []

    parents = [Optional('root.ul'), Optional('root.ol')]

    def render_main(self):
        return f'<li>{self.content}</li>'


@def_tag_set.register()
class UnorderedList(List):
    tag_name = 'ul'

@def_tag_set.register()
class OrderedList(List):
    tag_name = 'ol'
