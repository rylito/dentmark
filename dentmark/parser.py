import io
#from dentmark.element_node import ElementNode
from dentmark.text_node import TextNode

# special character constants
NEWLINE = '\n'
TAB = '\t'
SPACE = ' '
TRIM = '-'
COMMENT = '#'
ELEMENT_DELIM = ':'
VALID_NAME_CHARS = 'abcdefghijklmnopqrstuvwxyz01234567890_'

# special tags (get this from settings in the future?)
#PRE = 'pre'

class Parser:
    def __init__(self, defs_manager, flo_or_str):
        self.defs_manager = defs_manager
        #self.flo_or_str = flo_or_str
        #self.template_manager = template_manager
        #self.is_str = type(flo_or_str) is str
        #print(self.is_str, type(file_name_or_str))
        self.stream = io.StringIO(flo_or_str) if type(flo_or_str) is str else flo_or_str


    def _each_char(self):
        line_no = 1
        indent_level = 0
        count_whitespace = True
        self.is_comment = False

        #flo = io.StringIO(self.file_name_or_str) if self.is_str else open(self.file_name_or_str, 'r')
        #flo = io.StringIO(self.file_name_or_str) if self.is_str else self.file_name_or_str

        #with open(self.file_name, 'r') as f:
        with self.stream as f:
            while True:
                c = f.read(1)
                if not c:
                    break
                elif c == NEWLINE:
                    line_no += 1
                    indent_level = 0
                    count_whitespace = True
                    self.is_comment = False
                    if not self.pre_mode:
                        continue
                elif self.is_comment:
                    continue
                elif c in (SPACE, TAB) and count_whitespace:
                    indent_level += 1
                    if not self.pre_mode:
                        continue
                elif count_whitespace:
                    count_whitespace = False
                    if c == COMMENT and not self.pre_mode:
                        self.is_comment = True
                        continue
                yield (line_no, indent_level, c)


    def _new_line(self, c):
        self.line_accum = ''
        self.name_accum = ''
        self.first_accum = ''
        self.track_name = True
        self.is_element = False
        self.trim_left = (c == TRIM)
        self.trim_right = False


    def _rollup(self):
        popped = self.stack.pop()
        tail = self.stack[-1]
        tail.children.append(popped)
        return popped


    def _indentation_error(self, line_no):
        raise Exception(f'Indentation Error: line {line_no}')


    def _append_stack(self, prev_indent_level, indent_level, prev_line_no, line_no):

        if indent_level < self.lowest_indent:
            self._indentation_error(line_no)

        if self.prev_processed is not None:
            if self.prev_processed.is_element:
                if self.prev_processed.indent_level == prev_indent_level:
                    self._rollup()
            else:
                if prev_indent_level > self.prev_processed.indent_level:
                    self._indentation_error(prev_line_no)

        parent_node = self.stack[-1]
        child_order = len(parent_node.children)

        if self.is_element:
            #print('about to add', self.name_accum, 'last_stack_item', parent_node.name, 'count', child_order)
            #template = self.template_manager.get_template(self.name_accum)
            #if template is None:
                #raise Exception(f'Template Does Not Exist For Element')
                #print(f'Template Does Not Exist For Element (Assuming ctx for parent): {self.name_accum}')
            #node = ElementNode(prev_line_no, prev_indent_level, parent_node, child_order, self.name_accum, self.trim_left, self.trim_right)

            #print('PARENT', parent_node.tag_def.tag_name, 'CHILD', self.name_accum, 'IS_ALLOWED', parent_node.tag_def.is_child_allowed(self.name_accum))

            tag_def = self.defs_manager.get_def(self.name_accum)
            if tag_def is None:
                raise Exception(f'Invalid tag on line {prev_line_no}. Definition for tag does not exist: {self.name_accum}')
            #except KeyError:
                ##print('do it')
                #print(e)
                #raise Exception('I ')

            if not parent_node.is_child_allowed(self.name_accum):
                raise Exception(f"Child tag '{tag_def.tag_name}' on line {prev_line_no} not allowed for parent tag '{parent_node.tag_name}'")

            #node = ElementNode(prev_line_no, prev_indent_level, parent_node, child_order, tag_def, self.trim_left, self.trim_right)

            prev_count = self.counts.get(self.name_accum, 0)
            self.counts[self.name_accum] = prev_count + 1

            node = tag_def(prev_line_no, prev_indent_level, parent_node, child_order, prev_count, self.trim_left, self.trim_right)

            text = None
            if self.pre_text_pending:
                text = self._adjust_pre(self.line_accum, indent_level)
                self.pre_text_pending = False
                #print('print shit')
                #print(repr(text))
            else:
                first_element = self.first_accum.strip()
                if first_element != '':
                    text = first_element
            if text is not None:
                #print('putting', prev_line_no, prev_indent_level)
                node.children.append(TextNode(prev_line_no, prev_indent_level, node, 0, text))


            self.stack.append(node)

        else:
            node = TextNode(prev_line_no, prev_indent_level, parent_node, child_order, self.line_accum)
            parent_node.children.append(node)
            #print('text_node', self.line_accum, 'parent', parent_node.name, 'ord', child_order)

        self.prev_processed = node

        if indent_level < prev_indent_level:
            traverse_indent = prev_indent_level
            while indent_level < traverse_indent:
                popped = self._rollup()
                traverse_indent = popped.indent_level

            if traverse_indent != indent_level:
                self._indentation_error(line_no)

        # add the last remaining element child at first level (if any)
        if line_no is None and len(self.stack) > 1:
            self._rollup()


    def _check_name(self, c, is_start_of_line):
        if c == ELEMENT_DELIM:
            # validate name
            #print('GOOD NAME', self.name_accum, self.trim_left, self.trim_right)
            self.track_name = False
            self.is_element = True
            #if self.name_accum == PRE:
            if self.name_accum in self.defs_manager.pre_tag_names:
                self.pre_mode = True
        elif c == TRIM:
            if not is_start_of_line:
                if self.trim_right:
                    # two --
                    self.track_name = False
                    #print('2 dashes fail')
                else:
                    self.trim_right = True
        elif c not in VALID_NAME_CHARS:
            # some invalid name char
            self.track_name = False
            #print('invalid char in name')
        else:
            if self.trim_right:
                # trailing char after the last dash
                self.track_name = False
                #print('trailing char after the last dash')
            else:
                self.name_accum += c


    def _adjust_pre(self, pre_text, trailing_indent):
        # the +1 is to remove the trailing \n
        pre_text = pre_text[:-(trailing_indent + 1)]
        pre_text_split = pre_text.splitlines()

        smallest = None
        ws_counts = []

        for i,x in enumerate(pre_text_split):
            if x == '':
                ws_counts.append(None)
                continue

            count = 0
            for c in x:
                if c == ' ':
                    count += 1

            if x.strip() != '':
                if smallest is None or count < smallest:
                    smallest = count

            ws_counts.append(count)

        for i,x in enumerate(ws_counts):
            if x is None:
                continue
            pre_text_split[i] = pre_text_split[i][smallest:]

        pre_text = '\n'.join(pre_text_split)

        #print(pre_text)
        return pre_text


    def parse(self):
        #root_template = self.template_manager.get_root_template()
        #self.stack = [ElementNode.root(self.defs_manager.root_def)]

        self.counts = {}

        self.stack = [self.defs_manager.root_def.init_as_root()]
        self.prev_processed = None
        self.lowest_indent = None

        self.pre_mode = False
        pre_mode_indent = None
        pre_mode_begin = False
        self.pre_text_pending = False

        prev_line_no = None
        prev_indent_level = None

        for line_no, indent_level, c in self._each_char():
            #print(line_no, indent_level, c)

            if self.pre_mode:

                if pre_mode_begin:
                    if indent_level <= pre_mode_indent and c not in (SPACE, TAB, NEWLINE):
                        #print('STOP THE PRESS')
                        #print('line_accum', self.line_accum)
                        #print(self.prev_processed.name)

                        self.pre_mode = False
                        pre_mode_indent = None
                        pre_mode_begin = False
                        self.pre_text_pending = True

                        if c == COMMENT:
                            self.is_comment = True
                            continue

                    else:
                        self.line_accum += c
                        #print('pre_mode_line_accum', self.line_accum)
                elif c == NEWLINE:
                    pre_mode_begin = True
                    self.line_accum = ''
                elif c not in (SPACE, TAB):
                    raise Exception(f'Inline content not allowed after tag with is_pre=True: line {line_no}')

                if self.pre_mode:
                    continue

            is_start_of_line = (line_no != prev_line_no)

            if is_start_of_line:

                if prev_indent_level is None:
                    self.lowest_indent = indent_level
                else:
                    #print('doing append stack', prev_indent_level, indent_level, prev_line_no, line_no, c)
                    self._append_stack(prev_indent_level, indent_level, prev_line_no, line_no)

                self._new_line(c)

            self.line_accum += c

            if self.track_name:
                self._check_name(c, is_start_of_line)
                if self.pre_mode:
                    pre_mode_indent = indent_level
                    #print('pre_mode prepared')
            elif self.is_element:
                self.first_accum += c

            prev_line_no = line_no
            prev_indent_level = indent_level

        # pick up last line
        self._append_stack(prev_indent_level, self.lowest_indent, prev_line_no, None)

        #print('lowest indent', self.lowest_indent)
        #print(self.stack, self.stack[-1].name)
        print(self.stack[0].walk())
        return self.stack[0]


#if __name__ == '__main__':
    #Parser('test5.txt').parse()
    ##parse('test.txt')
