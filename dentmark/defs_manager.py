DEFAULT_DEF_SET = 'default'

class DefSet:
    def __init__(self, tag_set_name):
        #self.registered_tags = {}
        self.tag_set_name = tag_set_name
        self.pre_tag_addresses = []
        self.root_def = None
        self.tag_dict = {}
        self._is_checked = False
        #self.tag_dict = self._build_tag_dict(defs_cls_list)
        #self._check()

        # {tag_address: {child_tag_name: relation}}
        self.children_relation_dict = {}


    #@property
    #def empty(self):
        #return not self.tag_dict

    # tag_name arg allows us to create tags dynamically (i.e. tags assigned named at parse time, so multiple tag names can use same cls)
    def register_tag(self, tag_cls, replace=False, tag_name=None):
        #print('registering', tag_cls)

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

        #self.tag_dict[use_name] = tag_cls

        #if tag_cls.is_pre:
            #self.pre_tag_addresses.append(tag_cls.tag_name)

        self._is_checked = False


    def remove_tag(self, tag_address):
        del self.tag_dict[tag_address]


    # decorator for convenience
    def register(self, replace=False):
        def inner(tag_cls):
            self.register_tag(tag_cls, replace)
            return tag_cls
        return inner





    #def _build_tag_dict(self, defs_cls_list):
        #tag_dict = {}
        #root_def = None

        #for tag_cls in defs_cls_list:

            #if not tag_cls.tag_name:
                #raise Exception(f"tag_name not defined for: '{tag_cls.__name__}'")

            #existing_tag_for_name = tag_dict.get(tag_cls.tag_name)
            #if existing_tag_for_name is not None:
                #raise Exception(f"Duplicate tag name '{tag_cls.tag_name}' defined by '{existing_tag_for_name.__name__}' and '{tag_cls.__name__}'")

            #if tag_cls.is_root:
                #if self.root_def:
                    #raise Exception(f"TagDef '{tag_cls.__name__}' has is_root=True but root tag '{self.root_def.__name__}' already found. There can only be one root def.")
                #else:
                    #self.root_def = tag_cls

            #tag_dict[tag_cls.tag_name] = tag_cls
            #if tag_cls.is_pre:
                #self.pre_tag_names.append(tag_cls.tag_name)
        #return tag_dict


    def check(self):
        if self._is_checked:
            return

        if not self.tag_dict:
            raise Exception(f"Tag set '{self.tag_set_name}' contains no TagDefs")

        #unique_addresses = set()
        children_relation_dict = {}

        for address, tag_def_cls in self.tag_dict.items():
            #tag_def.check(self.tag_dict)
            parts = address.split('.')
            for i in range(len(parts)):
                partial = '.'.join(parts[:i + 1])
                #unique_addresses.add(partial)
                if partial not in self.tag_dict:
                    raise Exception(f"TagDef parent relation error for '{tag_def_cls.__name__}': TagDef with address '{partial}' not registered")

            # make sure pre tags don't have children and build children_relation_dict
            for relation in tag_def_cls.parents:
                #print('CHECK THIS', relation.parent_tag_address, self.pre_tag_addresses)
                if relation.parent_tag_address in self.pre_tag_addresses:
                    pre_tag_def_cls = self.tag_dict[relation.parent_tag_address]
                    raise Exception(f"TagDef parent relation error for '{tag_def_cls.__name__}': '{relation.parent_tag_address}' refers to TagDef '{pre_tag_def_cls.__name__}' which has is_pre=True. Preformatted tags cannot have child elements")

                # resolve this way rather than using tag_def_cls.tag_name since tag name might be registered dynamically
                child_tag_name = parts[-1]

                children_relation_dict.setdefault(relation.parent_tag_address, {})[child_tag_name] = relation

            #if tag_def_cls.is_pre:
                #self.pre_tag_addresses.append()

        self.children_relation_dict = children_relation_dict

        #print(unique_addresses)
        #input('HOLD')

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
        #self._default_loaded = False

    def get_tag_set(self, tag_set_name=None):
        #print('get_tag_set_hit')
        if tag_set_name is None:
            tag_set_name = DEFAULT_DEF_SET

        tag_set = self.def_sets.setdefault(tag_set_name, DefSet(tag_set_name))

        #if tag_set_name == DEFAULT_DEF_SET:
            #if not self._default_loaded:
                # load the default tags
                #import dentmark.default_definitions
                #tag_set.check()
                #self._default_loaded = True

        return tag_set

    #def register_tag(self, def_set_name, tag_cls, replace=False):
        #defs_set = self.def_sets.setdefault(def_set_name, DefSet())
        #defs_set.register_tag(tag_cls, replace)

    #def register(self, def_set_name, replace=False):
        #def inner(cls):
            #print('in inner', cls)
            #print('replace', replace)
            #self.register_tag(cls, replace)
            #return cls
        #return inner

    def copy_tag_set(self, new_tag_set_name, from_tag_set_name=None):
        from_tag_set = self.def_sets.get(from_tag_set_name if from_tag_set_name is not None else DEFAULT_DEF_SET)

        if from_tag_set is None:
            raise Exception(f"Tag set '{from_tag_set_name}' does not exist to copy")

        #from_def_sets = from_tag_set.def_sets
        #new_def_sets = from_tag_set.def_sets.copy()

        new_tag_set = DefSet(new_tag_set_name)

        #for tag_address, tag_def_cls in from_tag_set.tag_dict.items():
        for tag_def_cls in set(from_tag_set.tag_dict.values()):
            #print('COPYING', tag_def_cls)
            new_tag_set.register_tag(tag_def_cls)

        #new_tag_set = DefSet(new_tag_set_name)
        #new_tag_set.tag_dict = from_tag_set.tag_dict.copy()

        self.def_sets[new_tag_set_name] = new_tag_set

        return new_tag_set
