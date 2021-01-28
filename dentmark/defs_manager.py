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

            if not tag_cls.tag_name:
                raise Exception(f"tag_name not defined for: '{tag_cls.__name__}'")

            existing_tag_for_name = tag_dict.get(tag_cls.tag_name)
            if existing_tag_for_name is not None:
                raise Exception(f"Duplicate tag name '{tag_cls.tag_name}' defined by '{existing_tag_for_name.__name__}' and '{tag_cls.__name__}'")

            if tag_cls.is_root:
                if self.root_def:
                    raise Exception(f"TagDef '{tag_cls.__name__}' has is_root=True but root tag '{self.root_def.__name__}' already found. There can only be one root def.")
                else:
                    self.root_def = tag_cls

            tag_dict[tag_cls.tag_name] = tag_cls
            if tag_cls.is_pre:
                self.pre_tag_names.append(tag_cls.tag_name)
        return tag_dict


    def _check(self):
        #tag_set = set(self.tag_dict.keys())
        for tag_def in self.tag_dict.values():
            tag_def.check(self.tag_dict)


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
