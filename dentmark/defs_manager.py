DEFAULT_DEF_SET = 'default'

class DefSet:
    def __init__(self, tag_set_name):
        self.tag_set_name = tag_set_name
        self.pre_tag_addresses = []
        self.root_def = None
        self.tag_dict = {}
        self._is_checked = False

        # {tag_address: {child_tag_name: relation}}
        self.children_relation_dict = {}


    # tag_name arg allows us to create tags dynamically (i.e. tags assigned named at parse time, so multiple tag names can use same cls)
    def register_tag(self, tag_cls, replace=False, tag_name=None):

        use_name = tag_cls.tag_name if tag_cls.tag_name is not None else tag_name

        if not use_name:
            raise Exception(f"tag_name not defined for: '{tag_cls.__name__}'")

        tag_cls.check(use_name)

        for address in tag_cls.addresses:
            if not replace:
                existing_tag_for_address = self.tag_dict.get(address)
                if existing_tag_for_address is not None:
                    raise Exception(f"Duplicate tag address '{address}' defined by '{existing_tag_for_address.__name__}' and '{tag_cls.__name__}'")

            self.tag_dict[address] = tag_cls

            if tag_cls.is_pre:
                self.pre_tag_addresses.append(address)

        if tag_cls.is_root():
            if self.root_def and not replace:
                raise Exception(f"TagDef '{tag_cls.__name__}' has no parents defined and is a root tag, but root tag '{self.root_def.__name__}' already found. There can only be one root def.")
            else:
                self.root_def = tag_cls


        self._is_checked = False


    def remove_tag(self, tag_address):
        del self.tag_dict[tag_address]


    # decorator for convenience
    def register(self, replace=False):
        def inner(tag_cls):
            self.register_tag(tag_cls, replace)
            return tag_cls
        return inner


    def check(self):
        if self._is_checked:
            return

        if not self.tag_dict:
            raise Exception(f"Tag set '{self.tag_set_name}' contains no TagDefs")

        children_relation_dict = {}

        for address, tag_def_cls in self.tag_dict.items():
            parts = address.split('.')
            for i in range(len(parts)):
                partial = '.'.join(parts[:i + 1])
                if partial not in self.tag_dict:
                    raise Exception(f"TagDef parent relation error for '{tag_def_cls.__name__}': TagDef with address '{partial}' not registered")

            # make sure pre tags don't have children and build children_relation_dict
            for relation in tag_def_cls.parents:
                if relation.parent_tag_address in self.pre_tag_addresses:
                    pre_tag_def_cls = self.tag_dict[relation.parent_tag_address]
                    raise Exception(f"TagDef parent relation error for '{tag_def_cls.__name__}': '{relation.parent_tag_address}' refers to TagDef '{pre_tag_def_cls.__name__}' which has is_pre=True. Preformatted tags cannot have child elements")

                # resolve this way rather than using tag_def_cls.tag_name since tag name might be registered dynamically
                child_tag_name = parts[-1]

                children_relation_dict.setdefault(relation.parent_tag_address, {})[child_tag_name] = relation


        self.children_relation_dict = children_relation_dict

        self._is_checked = True

    def is_pre(self, tag_address):
        return tag_address in self.pre_tag_addresses

    def get_def(self, tag_address):
        return self.tag_dict.get(tag_address)

    def get_children_relations(self, tag_address):
        return self.children_relation_dict.get(tag_address, {})


class DefsManager:
    def __init__(self):
        self.def_sets = {}

    def get_tag_set(self, tag_set_name=None):
        if tag_set_name is None:
            tag_set_name = DEFAULT_DEF_SET

        tag_set = self.def_sets.setdefault(tag_set_name, DefSet(tag_set_name))

        return tag_set

    def copy_tag_set(self, new_tag_set_name, from_tag_set_name=None):
        from_tag_set = self.def_sets.get(from_tag_set_name if from_tag_set_name is not None else DEFAULT_DEF_SET)

        if from_tag_set is None:
            raise Exception(f"Tag set '{from_tag_set_name}' does not exist to copy")

        new_tag_set = DefSet(new_tag_set_name)

        for tag_def_cls in set(from_tag_set.tag_dict.values()):
            new_tag_set.register_tag(tag_def_cls)

        self.def_sets[new_tag_set_name] = new_tag_set

        return new_tag_set
