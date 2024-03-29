import dentmark.default_definitions.anchor
import dentmark.default_definitions.annotation
import dentmark.default_definitions.headlines
import dentmark.default_definitions.emphasis
import dentmark.default_definitions.lists
import dentmark.default_definitions.tables
import dentmark.default_definitions.images
import dentmark.default_definitions.youtube

from dentmark.tag_def import TagDef, Optional, OptionalUnique, Required, RequiredUnique

from dentmark.dentmark import defs_manager
def_tag_set = defs_manager.get_tag_set()


@def_tag_set.register()
class Root(TagDef):
    tag_name = 'root'

    def render_main(self):
        body = f'{self.content}'

        fns = self.collectors.get('fn', [])
        fns_rendered = ''.join(fns)

        if fns_rendered:
            body += f'<section class="footnotes" role="doc-endnotes"><hr/><ol>{fns_rendered}</ol></section>'

        return body

@def_tag_set.register()
class Pre(TagDef):
    tag_name = 'pre'
    is_pre = True

    parents = [Optional('root')]

    def render_main(self):
        return f'<pre>{self.content}</pre>'

@def_tag_set.register()
class Paragraph(TagDef):
    tag_name = 'p'

    parents = [Optional('root'), Optional('root.bq')]

    def render_main(self):
        classes = ''
        if self.classes:
            class_str = ' '.join(self.classes)
            classes = f' class="{class_str}"'
        return f'<p{classes}>{self.content}</p>'

@def_tag_set.register()
class BlockQuote(TagDef):
    tag_name = 'bq'

    parents = [Optional('root'), Optional('root.p.a8n.fn'), Optional('root.bq.p.a8n.fn')]

    def render_main(self):
        return f'<blockquote>{self.content}</blockquote>'

@def_tag_set.register()
class HorizontalRule(TagDef):
    tag_name = 'hr'

    parents = [Optional('root')]

    #TODO maybe enforce that this can't have any text/children?
    def render_main(self):
        return '<hr/>'

@def_tag_set.register()
class Break(TagDef):
    tag_name = 'br'

    min_num_text_nodes = 0
    max_num_text_nodes = 0

    parents = [Optional('root'), Optional('root.p'), Optional('root.bq.p'), Optional('root.bq')]

    def render_main(self):
        return '<br/>'
