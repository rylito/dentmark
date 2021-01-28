from .anchor import AnchorTagDef, URLTagDef, URL2TagDef
from .annotation import AnnotationTagDef, FootNoteTagDef
from dentmark import TagDef

class RootTagDef(TagDef):
    tag_name = 'root'
    is_root = True
    allow_children = ['p', 'a', 'code']

    def render_main(self):
        #return 'This is the primary string of root'
        body = f'<root>{self.content}</root>'

        fns = self.collectors.get('fn', [])
        fns_rendered = ''.join(fns)

        #fns_rendered = ''
        #for fn in fns:
            #fns_rendered += fn.render(False)
            #fns_rendered += fn

        return f'{body}<footnotes>{fns_rendered}</footnotes>'

class PreTagDef(TagDef):
    tag_name = 'code'
    is_pre = True
    #is_root = True # for testing, remove this

    #def render_main(self):
        #return f'<p>{self.content}</p>'

class ParagraphTagDef(TagDef):
    tag_name = 'p'
    #exclude_children = []
    allow_children = ['a', 'a8n']
    #exclude_children = ['b']

    def render_main(self):
        return f'<p>{self.content}</p>'
        #return 'This is the primary string of p'

class ItalicTagDef(TagDef):
    tag_name = 'i'
    allow_children = []

    def render_main(self):
        return f'<i>{self.content}</i>'
        #return 'This is the primary string of i'

REGISTERED_TAGS = (
    RootTagDef,
    AnchorTagDef,
    URLTagDef,
    URL2TagDef,
    #AnotherAnchorTagDef
    PreTagDef,
    ParagraphTagDef,
    ItalicTagDef,
    AnnotationTagDef,
    FootNoteTagDef
)
