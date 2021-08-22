from abc import ABC, abstractmethod

class Type(ABC):
    @classmethod
    @abstractmethod
    def fmt(cls, str_val):
        pass

    @classmethod
    @abstractmethod
    def validate(cls, str_val):
        pass

class String(Type):
    @classmethod
    def fmt(cls, str_val):
        return str_val

    @classmethod
    def validate(cls, str_val):
        pass

class Integer(Type):
    @classmethod
    def fmt(cls, str_val):
        return int(str_val)

    @classmethod
    def validate(cls, str_val):
        int(str_val)


class Boolean(Type):
    TRUE_VALS = ('1', 'T', 'TRUE', 'Y', 'YES')
    FALSE_VALS = ('0', 'F', 'FALSE', 'N', 'NO')

    @classmethod
    def fmt(cls, str_val):
        return str_val.upper() in cls.TRUE_VALS

    @classmethod
    def validate(cls, str_val):
        if str_val.upper() not in (cls.TRUE_VALS + cls.FALSE_VALS):
            raise Exception('Invalid boolean value')


class SyntaxNodeMap:
    def __init__(self, node_list=None):
        #print('node_list:', node_list)
        self.node_map = {}
        self.text_node = None
        self.dynamic_name_node = None

        for node in (node_list or []):
            self.add(node)

    def get_node(self, name):
        print('get node for name', name)
        node = self.node_map.get(name.upper())
        if node is None:
            return self.dynamic_name_node
        return node

    def add(self, node):
        print('adding', node.name)
        #TODO check to make sure is_text_node and dynamic_name_node aren't already set
        # (guard against dupe defitions)
        if node.is_text_node:
            self.text_node = node
        elif node.dynamic_name:
            self.dynamic_name_node = node
        else:
            self.node_map[node.name.upper()] = node

        print('after add', self.node_map, self.text_node, self.dynamic_name_node)

    def get_required_children(self):
        required_set = set([child for child in self.node_map.values() if child.min > 0])
        #TODO scalars must have 1 required text node - enforce this
        for node in (self.text_node, self.dynamic_name_node):
            if node is not None and node.min > 0:
                required_set.add(node)
        return required_set

    '''
    def search_for_node(self, name):
        print('hit', self.node_map)
        for syntax_node in self.node_map.values():
            print('iter', syntax_node)
            found_node = syntax_node.search_for_node(name)
            if found_node is not None:
                return found_node

        return None
    '''


class SyntaxNode:
    def __init__(self):
        #self.children = []
        self.allowed_children = SyntaxNodeMap()
        self.min = 0
        self.max = None
        #self.is_abstract = True

        self.name = None
        self.dynamic_name = False
        self.scalar_type_cls = None
        #self.type_cls = String

        self.is_root = False
        self.is_pre = False

        #TODO enforce that allowed children can't mix pre-defined and varname nodes (or maybe allow this with pre-defined taking priority?

    @property
    def is_text_node(self):
        return self.name is None and not self.dynamic_name and not self.is_root

        #TODO error to have self.name and self.dynamic_name both True

    def get_required_children(self):
        return self.allowed_children.get_required_children()

    def __str__(self):
        if self.is_text_node:
            return '[text node]'
        elif self.dynamic_name:
            return '[dynamic name]'
        else:
            return self.name

    '''
    def search_for_node(self, name): # searches for a descendant node
        if name.upper() == self.name:
            return self
        else:
            print('in node', self.name, 'looking for', name)
            return self.allowed_children.search_for_node(name)
    '''

    '''
    def is_descendant_pre(self, name):
        node = self.search_for_node(name)
        if node is not None:
            print('Checking node', name, 'for pre')
            return node.is_pre
        return False
    '''






