from dentmark import TagDef

class YouTubeEmbed(TagDef):
    tag_name = 'youtube'
    allow_children = ['width', 'height']

    unique_children = ['width', 'height']

    min_num_children = 1
    max_num_children = 1

    def render_main(self):
        video_id = self.content

        src = f'https://www.youtube.com/embed/{video_id}'

        width = self.context.get('width') or 560
        height = self.context.get('height') or 315

        return f'<iframe width="{width}" height="{height}" src="{src}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen=""></iframe>'


class WidthContext(TagDef):
    tag_name = 'width'
    is_context = True
    allow_children = []

    min_num_children = 1
    max_num_children = 1


    def validate(self):
        val = self.get_data()
        if not val.isdigit():
            return f"Tag '{self.tag_name}' expects a positive integer"

class HeightContext(WidthContext):
    tag_name = 'height'
