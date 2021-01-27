class TextNode:
    is_element = False
    is_root = False
    def __init__(self, line_no, indent_level, parent, order, text):
        self.line_no = line_no
        self.indent_level = indent_level
        self.parent = parent
        self.order = order
        self.text = text

    def walk(self):
        return self.text

    def pre_render(self):
        return self

    def render(self, template_manager):
        return self.text

    @property
    def is_root(self):
        return False

