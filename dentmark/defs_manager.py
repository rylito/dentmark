class DefsManager:
    def __init__(self, defs_cls_list):
        #self.defs_class_list = defs_class_list
        self.registered_tags = defs_cls_list
        self.pre_tag_names = []
        self.root_def = None
        self.tag_dict = self._build_tag_dict(defs_cls_list)
        #self.root_def = RootTagDef()
        self._check()

    def _build_tag_dict(self, defs_cls_list):
        tag_dict = {}
        root_def = None

        for tag_cls in defs_cls_list:
            existing_tag_for_name = tag_dict.get(tag_cls.tag_name)
            if existing_tag_for_name is not None:
                raise Exception(f"Duplicate tag name '{tag_cls.tag_name}' defined by '{existing_tag_for_name.__name__}' and '{tag_cls.__name__}'")

            if tag_cls.is_root:
                if self.root_def:
                    raise Exception(f"'{tag_cls.__name__}' has is_root=True but root tag '{self.root_def.__name__}' already found. There can only be one root def.")
                else:
                    self.root_def = tag_cls

            tag_dict[tag_cls.tag_name] = tag_cls
            if tag_cls.is_pre:
                self.pre_tag_names.append(tag_cls.tag_name)
        return tag_dict


    def _check(self):
        #tag_set = set(self.tag_dict.keys())
        for tag_def in self.tag_dict.values():

            allow_val = tag_def.allow_children
            exclude_val = tag_def.exclude_children
            def_ref = f"TagDef '{tag_def.__name__}'"

            for val, attr in ((allow_val, 'allow_children'), (exclude_val, 'exclude_children')):
                if val is not None and type(val) not in (list, tuple):
                    raise Exception(f'{def_ref} specifies invalid value for {attr}. Must be None or tuple/list of tag names')

            if tag_def.is_pre:
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
                        if tag_name not in self.tag_dict:
                            attr_name = 'allow' if check_list is allow_val else 'exclude'
                            raise Exception(f"{def_ref} contains an undefined tag name in {attr_name}_children: '{tag_name}'")


    def get_def(self, tag_name):
        return self.tag_dict.get(tag_name)
        #try:
            #return self.tag_dict[tag_name]
        #except KeyError:
            #raise Exception(f'Invalid tag. Definition for tag does not exist: {tag_name}')


    #def is_child_allowed(self, parent_tag_name, child_tag_name):
        #parent_tag_def = self.tag_dict[parent_tag_name]
        #if parent_tag_def.is_pre:
            #return False
        #elif parent_tag_def.allow_children is not None:
            #return child_tag_name in parent_tag_def.allow_children
        #else:
            #return child_tag_name not in parent_tag_def.exclude_children
