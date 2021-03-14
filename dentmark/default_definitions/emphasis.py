from dentmark.tag_def import TagDef, Optional, OptionalUnique, Required, RequiredUnique

from dentmark.dentmark import defs_manager
def_tag_set = defs_manager.get_tag_set()


#@def_tag_set.register()
class Emphasis(TagDef):
    #allow_children = ['a', 'b', 's', 'i']

    parents = [Optional('root'), Optional('root.p'), Optional('root.a'), Optional('root.bq')]

    def render_main(self):
        return f'<{self.tag_name}>{self.content}</{self.tag_name}>'

@def_tag_set.register()
class Italic(Emphasis):
    tag_name = 'i'


@def_tag_set.register()
class Bold(Emphasis):
    tag_name = 'b'


@def_tag_set.register()
class StrikeThrough(Emphasis):
    tag_name = 's'

@def_tag_set.register()
class HighLight(TagDef):
    tag_name = 'hl'

    parents = [Optional('root'), Optional('root.p'), Optional('root.bq'), Optional('root.bq.p')]

    def render_main(self):
        nth_of_type = self.nth_of_type + 1
        span_id = f'hlref:{nth_of_type}'
        return f'<span class="highlight" id="{span_id}">{self.content}</span>'

