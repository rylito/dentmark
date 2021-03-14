from dentmark.tag_def import TagDef, Optional, OptionalUnique, Required, RequiredUnique

from dentmark.dentmark import defs_manager
def_tag_set = defs_manager.get_tag_set()



@def_tag_set.register()
class YouTubeEmbed(TagDef):
    tag_name = 'youtube'
    #allow_children = ['width', 'height']

    #unique_children = ['width', 'height']

    min_num_children = 1
    max_num_children = 1

    parents = [Optional('root')]

    def render_main(self):
        video_id = self.content

        src = f'https://www.youtube.com/embed/{video_id}'

        width = self.context.get('width') or 560
        height = self.context.get('height') or 315

        return f'<iframe width="{width}" height="{height}" src="{src}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen=""></iframe>'


@def_tag_set.register()
class WidthContext(TagDef):
    tag_name = 'width'
    is_context = True
    #allow_children = []

    min_num_text_nodes = 1
    max_num_text_nodes = 1

    parents = [OptionalUnique('root.youtube')]

    def validate(self):
        val = self.get_data()
        if not val.isdigit() or int(val) < 1:
            return f"Tag '{self.tag_name}' expects a positive integer >= 1"


@def_tag_set.register()
class HeightContext(WidthContext):
    tag_name = 'height'
