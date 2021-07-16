# load default tags by importing them
import dentmark.default_definitions


from dentmark.dentmark import defs_manager, parse, render, add_element
from dentmark.tag_def import TagDef, BoolTagDef, PosIntTagDef, Relation, Optional, OptionalUnique, Required, RequiredUnique

