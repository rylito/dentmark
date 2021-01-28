#from abc import ABC, abstractmethod

class TagDef:
    tag_name = None
    add_to_collector = False
    is_toc_section = False
    is_context = False
    is_pre = False
    is_root = False

    allow_children = None
    exclude_children = None

    # maybe use type or issubclasss instead?
    is_element = True

    #def __init__(self, content, context={}, trim_left=False, trim_right=False):
    def __init__(self, line_no, indent_level, parent, order, nth_of_type, trim_left, trim_right):
        #self.content = content
        #self.context = context
        self.trim_left = trim_left
        self.trim_right = trim_right

        self.line_no = line_no
        self.indent_level = indent_level
        self.parent = parent
        self.order = order
        self.nth_of_type = nth_of_type
        self.trim_left = trim_left
        self.trim_right = trim_right

        # modified directly
        self.children = []
        self.collectors = {}
        self.content = ''
        self.context = {}


    @classmethod
    def init_as_root(cls):
        if not cls.is_root:
            raise Exception(f"Cannot init non-root TagDef '{cls.__name__}' as root")
        return cls(None, None, None, 0, 0, False, False)


    @classmethod
    def is_child_allowed(cls, child_tag_name):
        #parent_tag_def = self.tag_dict[parent_tag_name]
        if cls.is_pre:
            return False
        elif cls.allow_children is not None:
            return child_tag_name in cls.allow_children
        else:
            return child_tag_name not in cls.exclude_children

    @classmethod
    def check(cls, tag_dict):
        allow_val = cls.allow_children
        exclude_val = cls.exclude_children

        def_ref = f"TagDef '{cls.__name__}'"

        for val, attr in ((allow_val, 'allow_children'), (exclude_val, 'exclude_children')):
            if val is not None and type(val) not in (list, tuple):
                raise Exception(f'{def_ref} specifies invalid value for {attr}. Must be None or tuple/list of tag names')

        if cls.is_pre:
            #if allow_val or (exclude_val is False) or (exclude_val and exclude_val_type is not bool):
            if allow_val or exclude_val is not None:
                raise Exception(f'{def_ref} has is_pre=True. Pre tags cannot have children and exclude all tags by default. Remove the allow/exclude_children values from this def to use the default or explicitly set allow_children=[]')
        elif allow_val is None and exclude_val is None:
            raise Exception(f'{def_ref} must specify a value for either allow_children OR exclude_children')
        elif (allow_val is not None and exclude_val is not None):
            raise Exception(f'{def_ref} must specify a value for either allow_children OR exclude_children, not both')
        else:
            check_list = allow_val or exclude_val
            if check_list:
                # TODO use set.difference for this?
                for tag_name in check_list:
                    if tag_name not in tag_dict:
                        attr_name = 'allow' if check_list is allow_val else 'exclude'
                        raise Exception(f"{def_ref} contains an undefined tag name in {attr_name}_children: '{tag_name}'")


    #TODO useful for debugging, but not actually used in the rendering process
    def walk(self):
        rep = ''
        for x in self.children:
            rep += x.walk() + ', '
        #return f'[{self.trim_left}, {self.name}, {self.trim_right}, {rep[:-2]}]'
        return f'[{self.tag_name}, {rep[:-2]}]'


    def process_data(self, data):
        return data


    def get_data(self):
        child_data = []
        for child in self.children:
            child_data.append(child.get_data())
        return {self.tag_name: self.process_data(child_data)}


    def pre_render(self, root):
        for child in self.children:
            child.pre_render(root)

        if self.is_context:
            self.parent.context.update(self.get_data())

        if self.add_to_collector:
            root.collectors.setdefault(self.tag_name, []).append(self.render(False))
        print(self.tag_name, self.context, self.collectors, self.order, self.nth_of_type)


    def render(self, main=True):
        rendered_children = []
        prev_child = None

        for child in self.children:
            child_rendered = child.render(main).strip()

            if child_rendered:
                no_whitespace = (prev_child and prev_child.trim_right) or child.trim_left
                if rendered_children and not no_whitespace:
                    rendered_children.append('\n')

                rendered_children.append(child_rendered)

            prev_child = child

        self.content = ''.join(rendered_children)
        return self.render_main() if main else self.render_secondary()


    #@abstractmethod
    def render_main(self):
        # TODO is this a sane default?
        return '' if self.is_context else self.content


    def render_secondary(self):
        # TODO is this a sane default?
        return self.render_main()
