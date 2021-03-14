from dentmark.tag_def import TagDef, Optional, OptionalUnique, Required, RequiredUnique

from dentmark.dentmark import defs_manager
def_tag_set = defs_manager.get_tag_set()


@def_tag_set.register()
class Annotation(TagDef):
    tag_name = 'a8n'
    #allow_children = ['fn']

    parents = [Optional('root.p'), Optional('root.bq')] #TODO maybe this can be root level as well? Maybe blockquote too?

    def render_main(self):
        nth_of_type = self.nth_of_type + 1
        sup_id = f'fnref:{nth_of_type}'
        href = f'#fn:{nth_of_type}'

        return f'<span class="annotation__underline">{self.content}</span><sup id="{sup_id}"><a href="{href}" class="footnote-ref" role="doc-noteref">[{nth_of_type}]</a></sup>'

@def_tag_set.register()
class FootNote(TagDef):
    tag_name = 'fn'
    add_to_collector = True
    #allow_children = ['a', 'i']

    parents = [Optional('root.p.a8n'), Optional('root.bq.a8n')]

    def render_main(self):
        return '' # don't render anything in-place

    def render_secondary(self):
        nth_of_type = self.nth_of_type + 1
        fn_id = f'fn:{nth_of_type}'
        href = f'#fnref:{nth_of_type}'
        return f'<li id="{fn_id}" role="doc-endnote"><p><a href="{href}" class="footnote-backref" role="doc-backlink">↩︎</a> {self.content}</p></li>'
