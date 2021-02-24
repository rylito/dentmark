from dentmark.tag_def import TagDef

from dentmark.dentmark import defs_manager
def_tag_set = defs_manager.get_tag_set()



@def_tag_set.register()
class Image(TagDef):
    tag_name = 'img'
    # NOTE title already defined in anchor.TitleContext.
    # We can just re-use this context tag here since it has
    # the same configuration
    allow_children = ['title', 'alt']

    unique_children = ['title', 'alt']

    min_num_children = 1
    max_num_children = 1

    def render_main(self):
        # use first child as src
        src = self.content

        attrs = ''
        for ctx in ('title', 'alt'):
            ctx_val = self.context.get(ctx)
            if ctx_val:
                attrs += f' {ctx}="{ctx_val}"'

        return f'<img src="{src}"{attrs} />'


@def_tag_set.register()
class AltContext(TagDef):
    tag_name = 'alt'
    is_context = True
    allow_children = []

    min_num_children = 1
    max_num_children = 1

