import io
import re
from dentmark.text_node import TextNode

# special character constants
NEWLINE = '\n'
TAB = '\t'
SPACE = ' '
TRIM = '-'
COMMENT = '#'
ELEMENT_DELIM = ':'
VALID_NAME_CHARS = 'abcdefghijklmnopqrstuvwxyz01234567890_-'



class Parser:
    def __init__(self, defs_set, flo_or_str, extra_context):
        self.defs_set = defs_set
        self.stream = io.StringIO(flo_or_str) if type(flo_or_str) is str else flo_or_str
        self.extra_context = extra_context


    def _each_char(self):
        line_no = 1
        indent_level = 0
        count_whitespace = True
        self.is_comment = False

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
        self.escaped = False


    def _rollup(self):
        popped = self.stack.pop()
        children_relations = self.defs_set.get_children_relations(popped.address)
        #print('checking for tag', popped.address)
        #print('prev_processed', self.prev_processed)
        popped.check_children(children_relations)
        #if self.stack: # if only_address is used, there might not be anything else left on stack
        tail = self.stack[-1]
        tail.children.append(popped)
        return popped


    def _indentation_error(self, line_no):
        raise Exception(f'Indentation Error: line {line_no}')


    def _append_stack(self, prev_indent_level, indent_level, prev_line_no, line_no):

        parent_node = self.stack[-1]
        tag_address = f'{parent_node.address}.{self.name_accum}'
        if self.only_address and not tag_address.startswith(self.only_address):
            #print('rejecting this tag', self.only_address, tag_address)
            return


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
        root = self.stack[0]

        if self.is_element:
            #tag_address = self._get_address()
            tag_address = f'{parent_node.address}.{self.name_accum}'
            #if self.only_address and not tag_address.startswith(self.only_address):
                #print('rejecting this tag', self.only_address, tag_address)
                #return

            #tag_def = self.defs_set.get_def(self.name_accum, parent_node)
            tag_def = self.defs_set.get_def(tag_address)
            #print(self.stack)
            #print(tag_address, tag_def)
            #input('HOLD')
            if tag_def is None:
                raise Exception(f'Invalid tag on line {prev_line_no}. Definition for tag does not exist: {tag_address}')

            #if not parent_node.is_child_allowed(self.name_accum):
                #raise Exception(f"Child tag '{self.name_accum}' on line {prev_line_no} not allowed for parent tag '{parent_node.tag_name}'")

            #TODO do we want to base the counts on the name_accum or the address? for now, just go off name_accum
            prev_count = self.counts.get(self.name_accum, 0)
            self.counts[self.name_accum] = prev_count + 1

            node = tag_def(self.name_accum, tag_address, prev_line_no, prev_indent_level, parent_node, root, child_order, prev_count, self.trim_left, self.trim_right, self.extra_context)

            text = None
            if self.pre_text_pending:
                text = self._adjust_pre(self.line_accum, indent_level)
                self.pre_text_pending = False
            else:
                first_element = self.first_accum.strip()
                if first_element != '':
                    text = first_element
            if text is not None:
                node.children.append(TextNode(prev_line_no, prev_indent_level, node, root, 0, text, False, self.extra_context))


            self.stack.append(node)

        else:
            # use strip() here to remove any leading whitespace on escaped lines, i.e.
            #
            # p:
            #     : sarah: hello
            #     : bob: hello
            #      ^ strip this
            text = self.line_accum.strip()

            node = TextNode(prev_line_no, prev_indent_level, parent_node, root, child_order, text, self.escaped, self.extra_context)
            parent_node.children.append(node)

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


    def _check_name(self, c, is_start_of_line, indent_level):
        if c == ELEMENT_DELIM:
            # validate name
            self.track_name = False

            # Don't treat as tag if only ':'.
            # Trim ':' and treat as line so that text
            # lines that start with non-tag names can be escaped. For example:
            #
            # p:
            #    : bob: Hello
            #    br:
            #    : sarah: Hi Bob!

            if self.name_accum == '':
                # just reset line_accum to drop the ':'
                self.escaped = True
                self.line_accum = ''
            else:
                self.is_element = True

                # remove trailing '-' from name if present
                if self.name_accum[-1] == TRIM:
                    self.name_accum = self.name_accum[:-1]


                #print(self.name_accum)
                #print('MY STACK IS',self.stack)
                parent = self.stack[-1]
                if parent.indent_level == indent_level:
                    parent = self.stack[-2] # Fixes bug where this incorrectly nests element and gives wrong address prior to _rollup being called
                address = f'{parent.address}.{self.name_accum}'
                #print('PREV PROC', self.prev_processed, self.prev_processed.indent_level if self.prev_processed else None)
                #print('INDENT_LEVEL', indent_level)
                #print('ADDRESS', address)
                #input('HOLD')
                #print('.'.join([x.tag_name for x in self.stack]))
                #print(self._get_address())
                #print(self.defs_set.is_pre(self._get_address()))
                #input('HOLD')

                #if self._get_address() in self.defs_set.pre_tag_names:

                if self.defs_set.is_pre(address):
                    self.pre_mode = True
        elif c == TRIM:
            if not is_start_of_line:
                self.trim_right = True
                self.name_accum += c
        elif c not in VALID_NAME_CHARS:
            # some invalid name char
            self.track_name = False
        else:
            self.trim_right = False
            self.name_accum += c


    def _adjust_pre(self, pre_text, trailing_indent):
        if trailing_indent:
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
                else:
                    break

            if x.strip() != '':
                if smallest is None or count < smallest:
                    smallest = count

            ws_counts.append(count)

        for i,x in enumerate(ws_counts):
            if x is None:
                continue
            pre_text_split[i] = pre_text_split[i][smallest:]

        pre_text = '\n'.join(pre_text_split)

        return pre_text


    # only_address limits the parsing to only that address and any subchildren.
    # Used for partial rendering (i.e. extracting metadata without rendering entire document)
    def parse(self, only_address=None):
        # make sure def set is checked
        self.only_address = only_address

        self.defs_set.check()

        self.counts = {}

        self.stack = [self.defs_set.root_def.init_as_root(self.extra_context)]
        self.prev_processed = None
        self.lowest_indent = None

        self.pre_mode = False
        pre_mode_indent = None
        pre_mode_begin = False
        self.pre_text_pending = False

        prev_line_no = None
        prev_indent_level = None

        for line_no, indent_level, c in self._each_char():

            if self.pre_mode:

                if pre_mode_begin:
                    if indent_level <= pre_mode_indent and c not in (SPACE, TAB, NEWLINE):

                        self.pre_mode = False
                        pre_mode_indent = None
                        pre_mode_begin = False
                        self.pre_text_pending = True

                        if c == COMMENT:
                            self.is_comment = True
                            continue

                    else:
                        self.line_accum += c
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
                    self._append_stack(prev_indent_level, indent_level, prev_line_no, line_no)

                self._new_line(c)

            self.line_accum += c

            if self.track_name:
                self._check_name(c, is_start_of_line, indent_level)
                if self.pre_mode:
                    pre_mode_indent = indent_level
            elif self.is_element:
                self.first_accum += c

            prev_line_no = line_no
            prev_indent_level = indent_level

        # pick up last line
        if prev_line_no:
            if self.pre_mode:
                self.pre_text_pending = True
            self._append_stack(prev_indent_level, self.lowest_indent, prev_line_no, None)

        children_relations = self.defs_set.get_children_relations(self.stack[0].address)
        self.stack[0].check_children(children_relations) # check the root node to make sure its children are valid

        return self.stack[0]
