#from dentmark.tag_def import TagDef

#class RootTagDef(TagDef):
    #tag_name = 'root'

class ElementNode:
    is_element = True
    #def __init__(self, line_no, indent_level, parent, order, tag_def, trim_left, trim_right, is_root=False):
    def __init__(self, line_no, indent_level, parent, order, tag_def, trim_left, trim_right):
        self.line_no = line_no
        self.indent_level = indent_level
        self.parent = parent
        self.order = order
        self.tag_def = tag_def
        self.trim_left = trim_left
        self.trim_right = trim_right
        #self.is_root = is_root
        self.children = []

        self.ctx = {}

    @property
    def is_root(self):
        return self.tag_def.is_root

    @classmethod
    def root(cls, root_tag_def):
        return cls(None, None, None, 0, root_tag_def, False, False) #, True) #TODO FIX_ME

    def walk(self):
        rep = ''
        for x in self.children:
            rep += x.walk() + ', '
        #return f'[{self.trim_left}, {self.name}, {self.trim_right}, {rep[:-2]}]'
        print(self.tag_def)
        return f'[{self.tag_def.tag_name}, {rep[:-2]}]'

    def pre_render(self):
        content = []
        for child in self.children:
            tag_def_inst = child.pre_render()
            context = {}
        return self.tag_def(content, {}, self.trim_left, self.trim_right)

    def render(self):
        content = ''
        for child in self.children:
            child_content = child.render()
            #if child_content:
                #content.append(child_content)
            content += child_content
        return 

        #tag_def_inst = self.tag_def()

        #has_template = template_manager.has_template(self)
        #context = {'content': content, 'ctx': self.ctx}
        #rendered = template_manager.render(self, context)
        #if rendered is None:
            #raise Exception(f'Template Does Not Exist For Element')
            #print(f'Template Does Not Exist For Element (Assuming ctx for parent): {self.name}')
            #self.parent.ctx[self.name] = content
            #return None
        #else:
            #context = {'content': content, 'ctx': self.ctx}
            #return self.template.render(context).strip()
            #pass
        #return rendered

