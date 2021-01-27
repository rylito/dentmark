from dentmark import TagDef

class AnnotationTagDef(TagDef):
    tag_name = 'a8n'
    allow_children = ['fn']

    def primary(self):
        #nth_of_type = self.nth_of_type + 1
        #sup_id = f'fnref:{nth_of_type}'
        #href = f'#fn:{nth_of_type}'

        #return InlineFragment('annotation',
            #Inline('span', {'class': 'annotation__underline'}, self.content),
            #E('sup', {'id': sup_id},
                #Inline('a', {'href': href, 'class': 'footnote-ref', 'role': 'doc-noteref'},
                    #f'[{nth_of_type}]'
                #),
                #inline=True, trim_left=True
            #)
        #)
        return 'this is the primary string of a8n'


class FootNoteTagDef(TagDef):
    tag_name = 'fn'
    add_to_collector = True
    allow_children = ['a', 'i']

    def primary(self):
        #return Fragment('fn', self.content)
        return 'this is the primary string of fn'

    def secondary(self):
        #return Fragment('fn', self.content)
        #nth_of_type = self.nth_of_type + 1
        #fn_id = f'fn:{nth_of_type}'
        #href = f'#fnref:{nth_of_type}'
        #return E('li', {'id': fn_id, 'role': 'doc-endnote'},
            #E('p',
                #Inline('a', {'href': href, 'class': 'footnote-backref', 'role': 'doc-backlink'}, '↩︎'),
                #self.content
            #)
        #)
        return 'this is the secondary string of fn'




#<!-- annotate start --><a class="annotated" name="annotation_{{ nth_of_type }}">{{ content | safe}}</a><sup><a class="annotation" href="#note_{{ nth_of_type }}">[{{ nth_of_type }}]</a></sup><!-- annotate end -->

#<sup id="fnref:1"><a href="#fn:1" class="footnote-ref" role="doc-noteref">1</a></sup>
#nth_of_type
