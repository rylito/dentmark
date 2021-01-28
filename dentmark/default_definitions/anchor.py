from dentmark import TagDef

class AnchorTagDef(TagDef):
    tag_name = 'a'
    allow_children = ['url', 'i']
    #exclude_children = []

    def render_main(self):
        #return 'This is the primary string of a'
        url = self.context.get('url')
        return f'<a href="{url}">{self.content}</a>'

class URLTagDef(TagDef):
    tag_name = 'url'
    is_context = True
    allow_children = ['url2']

    def process_data(self, data):
        return 'processed ' + data[0]

class URL2TagDef(TagDef): #TODO delthis, after testing
    tag_name = 'url2'
    #is_context = True #TODO makes no difference, maybe note in docs about how any tag that is a child of a context tag also gets treated like context
    allow_children = []
