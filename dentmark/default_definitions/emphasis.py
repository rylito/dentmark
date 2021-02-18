from dentmark import TagDef

class Emphasis(TagDef):
    allow_children = ['a', 'b', 's', 'i']

    def render_main(self):
        return f'<{self.tag_name}>{self.content}</{self.tag_name}>'

class Italic(Emphasis):
    tag_name = 'i'


class Bold(Emphasis):
    tag_name = 'b'


class StrikeThrough(Emphasis):
    tag_name = 's'


