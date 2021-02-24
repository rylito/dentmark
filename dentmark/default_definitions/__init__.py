#from .anchor import Anchor, URLContext, TitleContext
import dentmark.default_definitions.anchor
#from .annotation import Annotation, FootNote
import dentmark.default_definitions.annotation
#from .headlines import H1, H2, H3, H4, H5, H6
import dentmark.default_definitions.headlines
#from .emphasis import Italic, Bold, StrikeThrough
import dentmark.default_definitions.emphasis
#from .lists import OrderedList, UnorderedList, ListItem
import dentmark.default_definitions.lists
#from .tables import Table, TableRow, TableCell, ColspanContext, RowspanContext, AlignContext
import dentmark.default_definitions.tables
#from .images import Image, AltContext
import dentmark.default_definitions.images
#from .youtube import YouTubeEmbed, WidthContext, HeightContext
import dentmark.default_definitions.youtube

from dentmark.tag_def import TagDef

from dentmark.dentmark import defs_manager
def_tag_set = defs_manager.get_tag_set()



@def_tag_set.register()
class Root(TagDef):
    tag_name = 'root'
    is_root = True
    exclude_children = [] # exclude nothing (allow everything)

    def render_main(self):
        body = f'{self.content}'

        fns = self.collectors.get('fn', [])
        fns_rendered = ''.join(fns)

        if fns_rendered:
            body += f'<section class="footnotes" role="doc-endnotes"><ol>{fns_rendered}</ol></section>'

        return body

@def_tag_set.register()
class Pre(TagDef):
    tag_name = 'pre'
    is_pre = True

    def render_main(self):
        return f'<pre>{self.content}</pre>'

@def_tag_set.register()
class Paragraph(TagDef):
    tag_name = 'p'
    exclude_children = ['p', 'li', 'bq']

    def render_main(self):
        return f'<p>{self.content}</p>'

@def_tag_set.register()
class BlockQuote(TagDef):
    tag_name = 'bq'
    allow_children = ['p', 'b', 's', 'i'] # TODO probably some others too

    def render_main(self):
        return f'<blockquote>{self.content}</blockquote>'

@def_tag_set.register()
class HorizontalRule(TagDef):
    tag_name = 'hr'
    allow_children = []

    #TODO maybe enforce that this can't have any text/children?
    def render_main(self):
        return '<hr/>'

@def_tag_set.register()
class Break(TagDef):
    tag_name = 'br'
    allow_children = []

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
