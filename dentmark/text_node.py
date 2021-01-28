class TextNode:
    is_element = False
    is_root = False

    #make this have the same interface as TagDef rather than having to test for is_element or type
    trim_left = False
    trim_right = False

    def __init__(self, line_no, indent_level, parent, order, text):
        self.line_no = line_no
        self.indent_level = indent_level
        self.parent = parent
        self.order = order
        self.text = text

    def walk(self):
        return self.text

    def get_data(self):
        return self.text

    def pre_render(self, root):
        #return self
        pass

    def render(self, main):
        #return f'{self.text}\n'
        #TODO process quotes, em dash, etc
        return self.text

    def to_dentmark(self, indent_level):
        tab = ' ' * (indent_level * 4)
        text = tab + self.text

        if self.parent.is_pre:
            split = self.text.split('\n')
            text = '\n'.join([tab + _ for _ in split])

        return text + '\n'
