from dentmark.tag_def import TagDef, Optional, OptionalUnique, Required, RequiredUnique

from dentmark.dentmark import defs_manager
def_tag_set = defs_manager.get_tag_set()



@def_tag_set.register()
class Image(TagDef):
    tag_name = 'img'

    #allow_children = ['title', 'alt']

    #unique_children = ['title', 'alt']

    min_num_text_nodes = 1
    max_num_text_nodes = 1

    parents = [Optional('root')]

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
class ImgAltContext(TagDef):
    tag_name = 'alt'
    is_context = True
    #allow_children = []

    min_num_text_nodes = 1
    max_num_text_nodes = 1

    parents = [OptionalUnique('root.img')]

@def_tag_set.register()
class ImgTitleContext(ImgAltContext):
    tag_name = 'title'

