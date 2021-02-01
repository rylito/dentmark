from dentmark import TagDef

class Anchor(TagDef):
    tag_name = 'a'
    allow_children = ['url', 'title', 'i', 'b', 's']
    #exclude_children = []

    def render_main(self):
        url = self.context.get('url')
        href = f' href="{url}"' if url else ''

        title = self.context.get('title')
        title_str = f' title="{title}"' if title else ''

        return f'<a{href}{title_str}>{self.content}</a>'

class URLContext(TagDef):
    tag_name = 'url'
    is_context = True
    allow_children = []

    #def process_data(self, data):
        # empty tag returns empty list
        #return (data and data[0]) or '' # use first value in list if it exists

class TitleContext(URLContext):
    tag_name = 'title'

