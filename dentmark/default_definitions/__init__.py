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
    #exclude_children = ['p', 'li', 'bq']

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
    #allow_children = ['p', 'b', 's', 'i'] # TODO probably some others too

    parents = [Optional('root'), Optional('root.p.a8n.fn')]

    def render_main(self):
        return f'<blockquote>{self.content}</blockquote>'

@def_tag_set.register()
class HorizontalRule(TagDef):
    tag_name = 'hr'
    #allow_children = []

    parents = [Optional('root')]

    #TODO maybe enforce that this can't have any text/children?
    def render_main(self):
        return '<hr/>'

@def_tag_set.register()
class Break(TagDef):
    tag_name = 'br'
    #allow_children = []

    parents = [Optional('root'), Optional('root.p'), Optional('root.bq.p'), Optional('root.bq')]

    #TODO maybe enforce that this can't have any text/children?
    def render_main(self):
        return '<br/>'

'''
REGISTERED_TAGS = (
    Root,
    H1, H2, H3, H4, H5, H6,
    Anchor, URLContext, TitleContext,
    Pre,
    Paragraph,
    Annotation, FootNote,
    Italic, Bold, StrikeThrough,
    OrderedList, UnorderedList, ListItem,
    Table, TableRow, TableCell, ColspanContext, RowspanContext, AlignContext,
    BlockQuote,
    HorizontalRule,
    Break,
    Image, AltContext,
    YouTubeEmbed, WidthContext, HeightContext,
)
'''
