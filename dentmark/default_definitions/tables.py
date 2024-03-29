from dentmark.tag_def import TagDef, Optional, OptionalUnique, Required, RequiredUnique

from dentmark.dentmark import defs_manager
def_tag_set = defs_manager.get_tag_set()


@def_tag_set.register()
class Table(TagDef):
    tag_name = 'table'

    min_num_text_nodes = 0
    max_num_text_nodes = 0

    parents = [Optional('root')]

    def render_main(self):
        return f'<table border="1">{self.content}</table>'


@def_tag_set.register()
class TableRow(TagDef):
    tag_name = 'tr'

    min_num_text_nodes = 0
    max_num_text_nodes = 0

    parents = [Required('root.table')]


    def render_main(self):
        return f'<tr>{self.content}</tr>'


@def_tag_set.register()
class TableCell(TagDef):
    tag_name = 'td'

    parents = [Required('root.table.tr')]


    def render_main(self):
        colspan = self.context.get('colspan')
        rowspan = self.context.get('rowspan')

        align = self.context.get('align')

        attrs = ''
        for ctx in ('colspan', 'rowspan', 'align'):
            ctx_val = self.context.get(ctx)
            if ctx_val:
                attrs += f' {ctx}="{ctx_val}"'

        return f'<td{attrs}>{self.content}</td>'


@def_tag_set.register()
class ColspanContext(TagDef):
    tag_name = 'colspan'
    is_context = True

    min_num_text_nodes = 1
    max_num_text_nodes = 1

    parents = [OptionalUnique('root.table.tr.td')]


@def_tag_set.register()
class RowspanContext(ColspanContext):
    tag_name = 'rowspan'


@def_tag_set.register()
class AlignContext(ColspanContext):
    tag_name = 'align'

    min_num_text_nodes = 1
    max_num_text_nodes = 1

    parents = [OptionalUnique('root.table.tr.td')]

    def process_data(self, data):
        return data[0].lower()

    def validate(self):
        val = self.get_data()

        if val not in ('left', 'right', 'center'):
            return 'value for align must be: left, right, or center'
