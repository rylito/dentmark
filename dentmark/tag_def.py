class Relation:
    # optional: (0 - many)
    #   min_count=0
    #   max_count=None
    #
    # unique optional: (0 - 1)
    #   min_count=0
    #   max_count=1
    #
    # required: (1 - many)
    #   min_count=1
    #   max_count=None
    #
    # unique required: (exactly 1)
    #   min_count=1
    #   max_count=1
    def __init__(self, parent_tag_address, min_count=0, max_count=None):
        self.parent_tag_address = parent_tag_address
        self.min_count = min_count
        self.max_count = max_count

    def check(self):
        if type(self.min_count) is not int or self.min_count < 0:
            raise Exception(f"Relation '{self.parent_tag_address}' min_count must be an int >= 0")

        if self.max_count is not None and ((type(self.max_count) is not int) or self.max_count < 0):
            raise Exception(f"Relation '{self.parent_tag_address}' max_count must be an int >= 0 or None")

        if self.max_count is not None and self.max_count < self.min_count:
            raise Exception(f"Relation '{self.parent_tag_address}' max_count of {self.max_count} is less than min_count of {self.min_count}")


# helper classes
class Optional(Relation):
    def __init__(self, parent_tag_address):
        super().__init__(parent_tag_address) # use Relation default args

class OptionalUnique(Relation):
    def __init__(self, parent_tag_address):
        super().__init__(parent_tag_address, max_count=1)

class Required(Relation):
    def __init__(self, parent_tag_address):
        super().__init__(parent_tag_address, min_count=1)

class RequiredUnique(Relation):
    def __init__(self, parent_tag_address):
        super().__init__(parent_tag_address, min_count=1, max_count=1)


class TagDef:
    tag_name = None
    add_to_collector = False
    is_context = False
    is_pre = False

    parents = []

    min_num_text_nodes = 0
    max_num_text_nodes = None

    is_element = True

    def __init__(self, tag_name, address, line_no, indent_level, parent, root, order, nth_of_type, trim_left, trim_right, extra_context):
        # tag_name defined on class, but passed in ctor in case inheriting classes want to do something custom with this
        # (i.e. dynamically create defs)
        self.address = address

        self.trim_left = trim_left
        self.trim_right = trim_right

        self.line_no = line_no
        self.indent_level = indent_level
        self.parent = parent
        self.root = root
        self.order = order
        self.nth_of_type = nth_of_type
        self.trim_left = trim_left
        self.trim_right = trim_right

        # modified directly
        self.children = []
        self.collectors = {}
        self.content = ''
        self.context = {}
        self.extra_context = extra_context

        self.tag_id = f'{self.tag_name}-{self.nth_of_type}'

        # can be used to modify HTML classes without having to override which is a common operation
        self.classes = []

    @classmethod
    def is_root(cls):
        return not cls.parents


    @classmethod
    def init_as_root(cls, extra_context):
        if not cls.is_root():
            raise Exception(f"Cannot init non-root TagDef '{cls.__name__}' as root")
        root_elem = cls(cls.tag_name, cls.tag_name, None, None, None, None, 0, 0, False, False, extra_context)
        root_elem.root = root_elem
        return root_elem


    @classmethod
    def check(cls, tag_name): # the tag_name can be set dynamically by overriding classes. If so, it will be passed here so the address can be set correctly
        def_ref = f"TagDef '{cls.__name__}'"

        if type(cls.parents) not in (list,tuple):
            raise Exception(f"{def_ref} specifies invalid value '{cls.parents}' for parents. Must be tuple/list of Relation instances")

        declared_parent_tag_addresses = set()
        cls.addresses = [] if cls.parents else [tag_name]

        for relation in cls.parents:
            if relation.parent_tag_address in declared_parent_tag_addresses:
                raise Exception(f"{def_ref} specifies multiple parent relation instances for: '{relation.parent_tag_address}'")
            # check the relation instance
            try:
                relation.check()
            except Exception as e:
                raise Exception(f"{def_ref} contains error in parent reference: {e}")
            declared_parent_tag_addresses.add(relation.parent_tag_address)
            cls.addresses.append(f'{relation.parent_tag_address}.{tag_name}')


        # check min_num_text_nodes / max_num_text_nodes
        min_text_nodes = cls.min_num_text_nodes
        max_text_nodes = cls.max_num_text_nodes

        if type(min_text_nodes) is not int or min_text_nodes < 0:
            raise Exception(f'{def_ref} min_num_text_nodes must be an int >= 0')

        if max_text_nodes is not None and ((type(max_text_nodes) is not int) or max_text_nodes < 0):
            raise Exception(f'{def_ref} max_num_text_nodes must be an int >= 0 or None')

        if max_text_nodes is not None and max_text_nodes < min_text_nodes:
            raise Exception(f'{def_ref} max_num_text_nodes of {max_text_nodes} is less than min_num_text_nodes of {min_text_nodes}')


    #TODO useful for debugging, but not actually used in the rendering process
    def walk(self):
        rep = ''
        for x in self.children:
            rep += x.walk() + ', '
        return f'[{self.tag_name}, {rep[:-2]}]'


    # can be overriden to customize or perform additional formatting on context tags
    # (i.e. looking up urls based on blog entry PKs)
    def process_data(self, data):
        if self.max_num_text_nodes == 0:
            return None
        elif self.max_num_text_nodes == 1:
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


    # enforces required, unique children and min/max_num_text_nodes
    def check_children(self, child_relations):

        # {child_tag_name: count}
        child_defs = {}

        text_node_count = 0

        for child in self.children:
            if child.is_element:
                try:
                    child_defs[child.tag_name] += 1
                except KeyError:
                    child_defs[child.tag_name] = 1
            else:
                text_node_count += 1


        # check present children
        for tag_name, count in child_defs.items():
            relation = child_relations[tag_name]

            if count < relation.min_count:
                raise Exception(f"Tag '{self.tag_name}' has {count} children node(s) of '{tag_name}' but expects at least {relation.min_count}: line {self.line_no}")

            if relation.max_count is not None:
                if count > relation.max_count:
                    raise Exception(f"Tag '{self.tag_name}' has {count} children node(s) of '{tag_name}' but expects no more than {relation.max_count}: line {self.line_no}")

        # check for non-present children that are required (i.e. min_count > 0)
        for child_tag_name, relation in child_relations.items():
            if relation.min_count > 0:
                if child_tag_name not in child_defs:
                    raise Exception(f"Tag '{self.tag_name}' has 0 children nodes of '{child_tag_name}' but expects at least {relation.min_count}: line {self.line_no}")
        if text_node_count < self.min_num_text_nodes:
            raise Exception(f"Tag '{self.tag_name}' has {text_node_count} non-element children node(s) but expects at least {self.min_num_text_nodes}: line {self.line_no}")

        if self.max_num_text_nodes is not None:
            if text_node_count > self.max_num_text_nodes:
                raise Exception(f"Tag '{self.tag_name}' has {text_node_count} non-element children node(s) but expects no more than {self.max_num_text_nodes}: line {self.line_no}")

        validate = self.validate()
        if validate:
            raise Exception(f'{validate}: line {self.line_no}')


    # Can be overridden to customize or perform additional validation on the element after parsing
    # and before render. Called when .render() method is called
    # If it returns a non-empty string, an exception will be raised.
    # Useful to modify children elements before rendering self.content
    def before_render(self):
        pass


    def pre_render(self):
        for child in self.children:
            child.pre_render()

        if self.is_context:
            self.parent.context.update({self.tag_name: self.get_data()})

        if self.add_to_collector:
            self.root.collectors.setdefault(self.tag_name, []).append(self.render(False))


    # returns a string composed of just the textnodes of non-context children elements
    def strip_tags(self):
        stripped = []
        for child in self.children:
            if child.is_element:
                if child.is_context:
                    continue
                stripped.extend(child.strip_tags())
            else:
                stripped.append(child)
        return stripped


    def render(self, main=True):
        before_render = self.before_render()
        if before_render:
            raise Exception(f'before_render failed for tag {self.tag_name}: {before_render}')

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
        return '' if self.is_context else self.content


    def render_secondary(self):
        return self.render_main()


    def add_child_element(self, tag_address, value, tag_set_name=None):

        from dentmark.dentmark import defs_manager

        tag_set = defs_manager.get_tag_set(tag_set_name)
        tag_def = tag_set.get_def(tag_address)

        if tag_def is None:
            raise Exception(f"Not a defined tag address: {tag_address}")

        # TODO just use None for values that can't be calculated. A bit hackish, but will
        # be fine to just re-generate the dentmark code. Not going to render this tree
        tag_address = f'{self.parent.address}.{tag_def.tag_name}'
        tag_def_inst = tag_def(tag_def.tag_name, tag_address, None, None, self, self.root, len(self.children), None, False, False, self.extra_context)

        from dentmark.text_node import TextNode

        text_node_inst = TextNode(None, None, tag_def_inst, self.root, 0, value, False, self.extra_context)
        tag_def_inst.children.append(text_node_inst)
        self.children.append(tag_def_inst)

        tag_def_inst_relations = tag_set.get_children_relations(tag_def_inst.address)
        tag_def_inst.check_children(tag_def_inst_relations)

        children_relations = tag_set.get_children_relations(self.address)
        self.check_children(children_relations)


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


    # can be used to modify HTML classes without having to override which is a common operation
    def add_class(self, html_class_name):
        self.classes.append(html_class_name)


    def _sibling_helper(self, get_next):
        prev = None
        return_next = False
        for child in self.parent.children:
            if return_next:
                return child
            if child is self:
                if get_next:
                    return_next = True
                else:
                    return prev
            prev = child
        return None


    def next_sibling(self):
        return self._sibling_helper(True)


    def prev_sibling(self):
        return self._sibling_helper(False)


    # if tag_name arg is 'p' and self is 'h3'
    # h3 (self), img, p(1), p(2) -> p(1)
    # h3 (self), img, h3 -> None
    def next_tag_of_type(self, tag_name):
        start_search = False
        for child in self.parent.children:
            if child is self:
                start_search = True
                continue

            if child.is_element and start_search:
                if child.tag_name == tag_name:
                    return child
                elif child.tag_name == self.tag_name:
                    return None
        return None


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

            children_str += child.to_dentmark(indent_level + (not self.is_root()))

        tab = ' ' * (indent_level * 4)
        trim_left = '-' if self.trim_left else ''
        trim_right = '-' if self.trim_right else ''

        if self.is_root():
            return f'{children_str}'
        else:
            return f'{tab}{trim_left}{self.tag_name}{trim_right}:{children_str}'


# TagDef helpers

# TODO make abc?
class BoolTagDef(TagDef):
    # tag_name should be set by inheriting class
    is_context = True

    min_num_text_nodes = 0
    max_num_text_nodes = 1

    def process_data(self, data):
        if data:
            return data[0].lower() == 'true'
        return True

    def validate(self):
        if self.children:
            if self.children[0].get_data().lower() not in ('true', 'false'):
                return f"'{self.tag_name}' tag value must be either 'true', 'false', or [empty]. Defaults to 'true' if [empty]"


# TODO make abc?
class PosIntTagDef(TagDef):
    # tag_name should be set by inheriting class
    is_context = True

    min_num_text_nodes = 1
    max_num_text_nodes = 1

    def process_data(self, data):
        val = int(data[0])
        if val < 1:
            raise ValueError
        return val


    def validate(self):
        try:
            self.get_data()
        except ValueError:
            return f"Tag '{self.tag_name}' expects a positive integer >= 1"
