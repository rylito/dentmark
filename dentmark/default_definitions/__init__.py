from .anchor import AnchorTagDef, URLTagDef
from .annotation import AnnotationTagDef, FootNoteTagDef
from dentmark import TagDef

class RootTagDef(TagDef):
    tag_name = 'root'
    is_root = True
    allow_children = ['p', 'a']

    def primary(self):
        return 'This is the primary string of root'

class PreTagDef(TagDef):
    tag_name = 'pre'
    is_pre = True
    #is_root = True # for testing, remove this

    def primary(self):
        return 'This is the primary string of pre'

class ParagraphTagDef(TagDef):
    tag_name = 'p'
    #exclude_children = []
    allow_children = ['a', 'a8n']
    #exclude_children = ['b']

    def primary(self):
        return 'This is the primary string of p'

class ItalicTagDef(TagDef):
    tag_name = 'i'
    allow_children = []

    def primary(self):
        return 'This is the primary string of i'

REGISTERED_TAGS = (
    RootTagDef,
    AnchorTagDef,
    URLTagDef,
    #AnotherAnchorTagDef
    PreTagDef,
    ParagraphTagDef,
    ItalicTagDef,
    AnnotationTagDef,
    FootNoteTagDef
)
