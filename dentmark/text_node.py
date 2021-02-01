import re

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
        self.text = str(text) # make sure this is always a str to avoid errors when inserting/adding

    def walk(self):
        return self.text

    def get_data(self):
        return self.text

    def pre_render(self, root):
        # Nothing needs to be done here, but method necessary since TextNode and TagDef have same interface
        pass

    def render(self, main):
        return self.get_enhanced_text()

    def get_enhanced_text(self):
        # Inserts 'fancy' left and right quotes as well as some other typographic enhancements

        # TODO there's probably a more sophisticated way to do this.
        # This seems to work OK for now.

        def replace_left(text, is_single):
            pattern = rf"\s'" if is_single else rf'\s"'
            split = list(text)
            for match in re.finditer(pattern, text):
                split[match.start()+1] = '&lsquo;' if is_single else '&ldquo;'

            return ''.join(split)

        escaped = self.text

        # Replace ' or " with an opening quote if it is the first character in the string
        escaped = re.sub(r'^"', '&ldquo;', escaped)
        escaped = re.sub(r"^'", '&lsquo;', escaped)

        # Now replace any ' or " with an opening quote if it is preceeded by whitespace.
        # The assumption here is that an opening quote will be preceeded by whitespace
        # while a closing one will not. i.e.: The boy says, "I can run fast!"
        escaped = replace_left(escaped, True)
        escaped = replace_left(escaped, False)

        # Replace any remaining ' or " with a closing (right) quote
        escaped = escaped.replace("'", '&rsquo;')
        escaped = escaped.replace('"', '&rdquo;')

        # Replace --- with emdash and ... with ellipsis
        escaped = escaped.replace('---', '&mdash;')
        escaped = escaped.replace('...', '&hellip;')

        return escaped


    def to_dentmark(self, indent_level):
        tab = ' ' * (indent_level * 4)
        text = tab + self.text

        if self.parent.is_pre:
            split = self.text.split('\n')
            text = '\n'.join([tab + _ for _ in split])

        return text + '\n'
