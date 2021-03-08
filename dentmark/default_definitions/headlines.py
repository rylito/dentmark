from dentmark.tag_def import TagDef, Optional, OptionalUnique, Required, RequiredUnique

from dentmark.dentmark import defs_manager
def_tag_set = defs_manager.get_tag_set()



#@def_tag_set.register()
class Headline(TagDef):
    #allow_children = []

    parents = [Optional('root')]

    def render_main(self):
        return f'<{self.tag_name}>{self.content}</{self.tag_name}>'


@def_tag_set.register()
class H1(Headline):
    tag_name = 'h1'


@def_tag_set.register()
class H2(Headline):
    tag_name = 'h2'


@def_tag_set.register()
class H3(Headline):
    tag_name = 'h3'


@def_tag_set.register()
class H4(Headline):
    tag_name = 'h4'


@def_tag_set.register()
class H5(Headline):
    tag_name = 'h5'


@def_tag_set.register()
class H6(Headline):
    tag_name = 'h6'
