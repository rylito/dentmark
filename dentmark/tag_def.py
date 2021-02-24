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

    required_children = []
    unique_children = []

    # does not include context tags in the count
    min_num_children = 0
    max_num_children = None


    # maybe use type or issubclasss instead?
    is_element = True

    def __init__(self, line_no, indent_level, parent, order, nth_of_type, trim_left, trim_right):
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
        self.extra_context = {}

        self.tag_id = f'{self.tag_name}-{self.nth_of_type}'


    @classmethod
    def init_as_root(cls):
        if not cls.is_root:
            raise Exception(f"Cannot init non-root TagDef '{cls.__name__}' as root")
        return cls(None, None, None, 0, 0, False, False)


    @classmethod
    def is_child_allowed(cls, child_tag_name):
        if cls.is_pre:
            return False
        elif cls.allow_children is not None:
            return child_tag_name in cls.allow_children
        else:
            return child_tag_name not in cls.exclude_children


    @classmethod
    def check(cls, tag_dict):
        def_ref = f"TagDef '{cls.__name__}'"

        allow_def = ('allow_children', cls.allow_children)
        exclude_def = ('exclude_children', cls.exclude_children)

        required_def = ('required_children', cls.required_children)
        unique_def = ('unique_children', cls.unique_children)

        def check_defined_tags(attr_name, tag_names):
            if tag_names:
                unknown_set = set(tag_names).difference(tag_dict)
                if unknown_set:
                    raise Exception(f"{def_ref} contains undefined tag names in {attr_name}: {unknown_set}")

        for attr_name, val in (allow_def, exclude_def, required_def, unique_def):
            if val is not None and type(val) not in (list, tuple):
                raise Exception(f'{def_ref} specifies invalid value for {attr_name}. Must be None or tuple/list of tag names')

        # check allow_children / exclude_children

        if cls.is_pre:
            #if allow_val or (exclude_val is False) or (exclude_val and exclude_val_type is not bool):
            if allow_def[1] or exclude_def[1] is not None:
                raise Exception(f'{def_ref} has is_pre=True. Pre tags cannot have children and exclude all tags by default. Remove the allow/exclude_children values from this def to use the default or explicitly set allow_children=[]')
        elif allow_def[1] is None and exclude_def[1] is None:
            raise Exception(f'{def_ref} must specify a value for either allow_children OR exclude_children')
        elif (allow_def[1] is not None and exclude_def[1] is not None):
            raise Exception(f'{def_ref} must specify a value for either allow_children OR exclude_children, not both')
        else:
            check_defined_tags(*(allow_def if allow_def[1] else exclude_def))

        # check required_children / unique_children agree with allow_children / exclude_children
        for attr_name, val in (required_def, unique_def):
            if val:
                # check that tag definiton exists
                check_defined_tags(attr_name, val)

                # check that it's allowed as a child
                for tag_name in val:
                    if not cls.is_child_allowed(tag_name):
                        raise Exception(f'{def_ref} specifies a child tag in {attr_name} that is not allowed as a child: {tag_name}')

        # check min_num_children / max_num_children
        min_children = cls.min_num_children
        max_children = cls.max_num_children

        if type(min_children) is not int or min_children < 0:
            raise Exception(f'{def_ref} min_num_children must be an int >= 0')

        if max_children is not None and ((type(max_children) is not int) or max_children < 0):
            raise Exception(f'{def_ref} max_num_children must be an int >= 0 or None')

        if max_children is not None and max_children < min_children:
            raise Exception(f'{def_ref} max_num_children of {max_children} is less than min_num_children of {min_children}')

        #num_required = len(required_def[1]) if required_def[1] else 0

        #if min_children < num_required:
            #raise Exception(f'{def_ref} min_num_children of {min_children} should be >= {num_required} since there are {num_required} {required_def[0]}')


    #TODO useful for debugging, but not actually used in the rendering process
    def walk(self):
        rep = ''
        for x in self.children:
            rep += x.walk() + ', '
        return f'[{self.tag_name}, {rep[:-2]}]'


    # can be overriden to customize or perform additional formatting on context tags
    # (i.e. looking up urls based on blog entry PKs)
    def process_data(self, data):
        if self.max_num_children == 0:
            return None
        elif self.max_num_children == 1:
            return data[0]
        else:
            return data


    # Can be overridden to customize or perform additional validation at parse time.
    # If it returns a non-empty string, an exception will be raised
    def validate(self):
        pass


    def get_data(self):
        child_data = []
        for child in self.children:
            child_data.append(child.get_data())
        #return {self.tag_name: self.process_data(child_data)}
        return self.process_data(child_data)


    # enforces required_children, unique_children, and min/max_num_children
    def check_children(self):
        seen = set()
        non_context_count = 0
        for child in self.children:
            if child.is_element:
                if child.tag_name in self.unique_children:
                    if child.tag_name in seen:
                        raise Exception(f"Tag '{self.tag_name}' does not allow multiple children of type '{child.tag_name}': line {child.line_no}")
                seen.add(child.tag_name)

                if child.is_context:
                    continue # do not add this to the count

            non_context_count += 1

        if self.required_children:
            missing = set(self.required_children).difference(seen)
            if missing:
                raise Exception(f"Tag '{self.tag_name}' missing required child tags {missing}: line {self.line_no}")

        if non_context_count < self.min_num_children:
            raise Exception(f"Tag '{self.tag_name}' has {non_context_count} non-context children nodes but expects at least {self.min_num_children}: line {self.line_no}")

        if self.max_num_children is not None:
            if non_context_count > self.max_num_children:
                raise Exception(f"Tag '{self.tag_name}' has {non_context_count} non-context children nodes but expects no more than {self.max_num_children}: line {self.line_no}")

        validate = self.validate()
        if validate:
            raise Exception(f'{validate}: line {self.line_no}')


    def pre_render(self, root, extra_context={}):
        for child in self.children:
            child.pre_render(root, extra_context)

        if self.is_context:
            self.parent.context.update({self.tag_name: self.get_data()})

        self.extra_context = extra_context

        if self.add_to_collector:
            root.collectors.setdefault(self.tag_name, []).append(self.render(False))


    def render(self, main=True):
        rendered_children = []
        prev_child = None

        for child in self.children:
            child_rendered = child.render(main)

            if child_rendered:
                no_whitespace = (prev_child and prev_child.trim_right) or child.trim_left
                if rendered_children and not no_whitespace:
                    rendered_children.append('\n')

                rendered_children.append(child_rendered)

            prev_child = child

        self.content = ''.join(rendered_children)
        return self.render_main() if main else self.render_secondary()


    def render_main(self):
        # TODO is this a sane default?
        return '' if self.is_context else self.content


    def render_secondary(self):
        # TODO is this a sane default?
        return self.render_main()

    def add_child_element(self, defs_manager, tag_name, value):

        tag_def = defs_manager.get_def(tag_name)
        if tag_def is None:
            raise Exception(f"Not a defined tag_name: {tag_name}")

        if tag_name not in self.allow_children:
            def_ref = f"TagDef '{self.__class__.__name__}'"

            raise Exception(f"Child tag '{tag_name}' not allowed as child of {def_ref}")

        # TODO just use None for values that can't be calculated. A bit hackish, but will
        # be fine to just re-generate the dentmark code. Not going to render this tree
        tag_def_inst = tag_def(None, None, self, len(self.children), None, False, False)

        from dentmark.text_node import TextNode

        text_node_inst = TextNode(None, None, tag_def_inst, 0, value)
        tag_def_inst.children.append(text_node_inst)
        self.children.append(tag_def_inst)


    def get_tag_by_id(self, tag_id):
        if self.tag_id == tag_id:
            return self

        for child in self.children:
            if not child.is_element:
                continue
            found_it = child.get_tag_by_id(tag_id)
            if found_it:
                return found_it
        return None


    def gen_tags_by_name(self, tag_name):
        if self.tag_name == tag_name:
            yield self

        for child in self.children:
            if not child.is_element:
                continue
            for found in child.gen_tags_by_name(tag_name):
                yield found

    def get_child_by_name(self, tag_name, return_multiple=False):
        multiple = []
        for child in self.children:
            if not child.is_element:
                continue
            if child.tag_name != tag_name:
                continue
            if not return_multiple:
                return child
            multiple.append(child)
        return multiple if return_multiple else None


    # experiment with generating dentmark markup from the tree,
    # so that eventually we can edit the tree, then output modified dentmark
    def to_dentmark(self, indent_level = 0):

        # make sure tags with no children like br: have a trailing newline
        children_str = '' if self.children else '\n'

        for i, child in enumerate(self.children):
            if i == 0:
                if (not self.is_pre) and (not child.is_element):
                    # If first child is a text node, print it inline with tag to preserve
                    # intentional 'tag masking' i.e. a: https://
                    # This also saves space anyways even if tag masking is not necessary.
                    children_str += f' {child.text}\n'
                    continue
                children_str += '\n'

            children_str += child.to_dentmark(indent_level + (not self.is_root))

        tab = ' ' * (indent_level * 4)
        trim_left = '-' if self.trim_left else ''
        trim_right = '-' if self.trim_right else ''

        if self.is_root:
            return f'{children_str}'
        else:
            return f'{tab}{trim_left}{self.tag_name}{trim_right}:{children_str}'
