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

    def __init__(self, content, context={}, trim_left=False, trim_right=False):
        self.content = content
        self.context = context
        self.trim_left = trim_left
        self.trim_right = trim_right

        #if self.tag_name is None: #TODO is this really the best way to enforce this?
            #raise Exception(f'TagDef instance must define tag_name: {self.__class__.__name__}')

        #for k,v in context.items():
            #if k == 'context':
                #TODO cannot have context variable named context
                #raise Exception("context key cannot be 'context'")
            #setattr(self,k,v)

    @classmethod
    def is_child_allowed(cls, child_tag_name):
        #parent_tag_def = self.tag_dict[parent_tag_name]
        if cls.is_pre:
            return False
        elif cls.allow_children is not None:
            return child_tag_name in cls.allow_children
        else:
            return child_tag_name not in cls.exclude_children


    #@abstractmethod
    def primary(self):
        return ''

"""
    def render_primary(self):
        src = self.primary()
        #TODO this will fail if it returns a string
        try:
            src.trim_left = self.trim_left
            src.trim_right = self.trim_right
        except:
            pass
        return src

    #@abstractmethod
    def render_secondary(self):
        return self.secondary()
        #return ''
"""

