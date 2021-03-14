from dentmark.tag_def import TagDef, Optional, OptionalUnique, Required, RequiredUnique

from dentmark.dentmark import defs_manager
def_tag_set = defs_manager.get_tag_set()



@def_tag_set.register()
class Anchor(TagDef):
    tag_name = 'a'

    #allow_children = ['url', 'title']

    #unique_children = ['url', 'title']

    #min_num_text_nodes = 1
    #max_num_text_nodes = 1

    parents = [Optional('root'), Optional('root.p'), Optional('root.p.a8n.fn'), Optional('root.bq.a8n.fn')]


    def render_main(self):
        url = self.context.get('url')
        if url is None:
            if self.content.startswith('http'):
                url = self.content

        href = f' href="{url}"' if url else ''

        title = self.context.get('title')
        title_str = f' title="{title}"' if title else ''

        return f'<a{href}{title_str}>{self.content}</a>'

@def_tag_set.register()
class URLContext(TagDef):
    tag_name = 'url'
    is_context = True
    #allow_children = []

    min_num_text_nodes = 1
    max_num_text_nodes = 1

    parents = [OptionalUnique('root.a'), OptionalUnique('root.p.a'), Optional('root.p.a8n.fn.a'), Optional('root.bq.a8n.fn.a')]

@def_tag_set.register()
class AnchorTitleContext(URLContext):
    tag_name = 'title'

    parents = [OptionalUnique('root.a'), OptionalUnique('root.p.a')]

