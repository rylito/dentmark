from dentmark import TagDef

class Table(TagDef):
    tag_name = 'table'
    allow_children = ['tr']

    def render_main(self):
        return f'<table border="1">{self.content}</table>'

class TableRow(TagDef):
    tag_name = 'tr'
    allow_children = ['td']

    def validate(self):
        for child in self.children:
            if not child.is_element:
                return 'tr tag does not allow text nodes. Only td tags are allowed as children'

    def render_main(self):
        return f'<tr>{self.content}</tr>'

class TableCell(TagDef):
    tag_name = 'td'

    #TODO probably should allow links and some other tags too
    allow_children = ['colspan', 'rowspan', 'align', 'a', 'b', 's', 'i']

    unique_children = ['colspan', 'rowspan', 'align']


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


class ColspanContext(TagDef):
    tag_name = 'colspan'
    is_context = True
    allow_children = []

    min_num_children = 1
    max_num_children = 1


class RowspanContext(ColspanContext):
    tag_name = 'rowspan'


class AlignContext(ColspanContext):
    tag_name = 'align'

    def process_data(self, data):
        return data[0].lower()

    def validate(self):
        val = self.get_data()

        if val not in ('left', 'right', 'center'):
            return 'value for align must be: left, right, or center'
