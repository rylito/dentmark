from dentmark import TagDef

class AnchorTagDef(TagDef):
    tag_name = 'a'
    allow_children = ['url', 'i']
    #exclude_children = []

    def primary(self):
        return 'This is the primary string of a'

class URLTagDef(TagDef):
    tag_name = 'url'
    is_context = True
    allow_children = []
