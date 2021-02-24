DEFAULT_DEF_SET = 'default'

class DefSet:
    def __init__(self, tag_set_name):
        #self.registered_tags = {}
        self.tag_set_name = tag_set_name
        self.pre_tag_names = []
        self.root_def = None
        self.tag_dict = {}
        self._is_checked = False
        #self.tag_dict = self._build_tag_dict(defs_cls_list)
        #self._check()


    #@property
    #def empty(self):
        #return not self.tag_dict

    def register_tag(self, tag_cls, replace=False):
        print('registering', tag_cls)

        if not tag_cls.tag_name:
            raise Exception(f"tag_name not defined for: '{tag_cls.__name__}'")

        if not replace:
            existing_tag_for_name = self.tag_dict.get(tag_cls.tag_name)
            if existing_tag_for_name is not None:
                raise Exception(f"Duplicate tag name '{tag_cls.tag_name}' defined by '{existing_tag_for_name.__name__}' and '{tag_cls.__name__}'")

        if tag_cls.is_root:
            if self.root_def and not replace:
                raise Exception(f"TagDef '{tag_cls.__name__}' has is_root=True but root tag '{self.root_def.__name__}' already found. There can only be one root def.")
            else:
                self.root_def = tag_cls

        self.tag_dict[tag_cls.tag_name] = tag_cls

        if tag_cls.is_pre:
            self.pre_tag_names.append(tag_cls.tag_name)

        self._is_checked = False


    def remove_tag(self, tag_name):
        del self.tag_dict[tag_name]


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

        for tag_def in self.tag_dict.values():
            tag_def.check(self.tag_dict)

        self._is_checked = True


    def get_def(self, tag_name):
        #assert self._is_checked, 'tags have not been checked. Danger everywhere.' #TODO DELME
        return self.tag_dict.get(tag_name)


class DefsManager:
    def __init__(self):
        self.def_sets = {}
        #self._default_loaded = False

    def get_tag_set(self, tag_set_name=None):
        print('get_tag_set_hit')
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

        for tag_name, tag_def_cls in from_tag_set.tag_dict.items():
            new_tag_set.register_tag(tag_def_cls)

        #new_tag_set = DefSet(new_tag_set_name)
        #new_tag_set.tag_dict = from_tag_set.tag_dict.copy()

        self.def_sets[new_tag_set_name] = new_tag_set

        return new_tag_set
