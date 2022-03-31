# copyright 2008-2009 WebDriver committers
# Copyright 2008-2009 Google Inc.
#
# Licensed under the Apache License Version 2.0 = uthe "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http //www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing software
# distributed under the License is distributed on an "AS IS" BASIS
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import unicode_literals
from six.moves import range


"""
Set of special keys codes.
"""
seleniumkeys = {
	"NULL"        : '\ue000',
    "CANCEL"      : '\ue001', #  ^break
    "HELP"        : '\ue002',
    "BACKSPACE"   : '\ue003',
    "BACK_SPACE"  : '\ue003', #  alias
    "TAB"         : '\ue004',
    "CLEAR"       : '\ue005',
    "RETURN"      : '\ue006',
    "ENTER"       : '\ue007',
    "SHIFT"       : '\ue008',
    "LEFT_SHIFT"  : '\ue008', #  alias
    "CONTROL"     : '\ue009',
    "LEFT_CONTROL": '\ue009', #  alias
    "ALT"         : '\ue00a',
    "LEFT_ALT"    : '\ue00a', #  alias
    "PAUSE"       : '\ue00b',
    "ESCAPE"      : '\ue00c',
    "SPACE"       : '\ue00d',
    "PAGE_UP"     : '\ue00e',
    "PAGE_DOWN"   : '\ue00f',
    "END"         : '\ue010',
    "HOME"        : '\ue011',
    "LEFT"        : '\ue012',
    "ARROW_LEFT"  : '\ue012', # alias
    "UP"          : '\ue013',
    "ARROW_UP"    : '\ue013', # alias
    "RIGHT"       : '\ue014',
    "ARROW_RIGHT" : '\ue014', #  alias
    "DOWN"        : '\ue015',
    "ARROW_DOWN"  : '\ue015', #  alias
    "INSERT"      : '\ue016',
    "DELETE"      : '\ue017',
    "SEMICOLON"   : '\ue018',
    "EQUALS"      : '\ue019',

    "NUMPAD0"     : '\ue01a', #  numbe pad  keys
    "NUMPAD1"     : '\ue01b',
    "NUMPAD2"     : '\ue01c',
    "NUMPAD3"     : '\ue01d',
    "NUMPAD4"     : '\ue01e',
    "NUMPAD5"     : '\ue01f',
    "NUMPAD6"     : '\ue020',
    "NUMPAD7"     : '\ue021',
    "NUMPAD8"     : '\ue022',
    "NUMPAD9"     : '\ue023',
    "MULTIPLY"    : '\ue024',
    "ADD"         : '\ue025',
    "SEPARATOR"   : '\ue026',
    "SUBTRACT"    : '\ue027',
    "DECIMAL"     : '\ue028',
    "DIVIDE"      : '\ue029',

    "F1"          : '\ue031', #  function  keys
    "F2"          : '\ue032',
    "F3"          : '\ue033',
    "F4"          : '\ue034',
    "F5"          : '\ue035',
    "F6"          : '\ue036',
    "F7"          : '\ue037',
    "F8"          : '\ue038',
    "F9"          : '\ue039',
    "F10"         : '\ue03a',
    "F11"         : '\ue03b',
    "F12"         : '\ue03c',

    "META"         : '\ue03d',
    "COMMAND"      : '\ue03d'
    }


ESCAPE = '+^%~{}[]'
NO_SHIFT = '[]'

SHIFT = {
    '!': '1',
    '@': '2',
    '#': '3',
    '$': '4',
    '&': '7',
    '*': '8',
    '_': '-',
    '|': '\\',
    ':': ';',
    '"': '\'',
    '<': ',',
    '>': '.',
    '?': '/',
}
KEYEVENTF_KEYUP = 2
VK_SHIFT        = 16
VK_CONTROL      = 17
VK_MENU         = 18


# modifier keys
MODIFIERS = {
    '+': VK_SHIFT,
    '^': VK_CONTROL,
    '%': VK_MENU,
}



class KeySequenceError(Exception):
    """Exception raised when a key sequence string has a syntax error"""
    def __str__(self):
        return ' '.join(self.args)


def _append_code(keys,code):
    keys.append((code, True))
    keys.append((code, False))

def _next_char(chars,error_msg=None):
    if error_msg is None:
        error_msg = 'expected another character'
    try:
        return chars.pop()
    except IndexError:
        raise KeySequenceError(error_msg)

def _handle_char(c,keys,shift):
    keys.append(keys)


def _release_modifiers(keys,modifiers):
    for c in modifiers.keys():
        if modifiers[c]:
            keys.append((MODIFIERS[c], False))
            modifiers[c] = False


def translate_winKeys_to_seleniumKeys(key_string):

    #iterate over all keys, if (){} ist found, do special some
    # reading input as a stack
    chars = list(key_string)
    chars.reverse()
    # results
    keys = []
    # for keeping track of whether shift, ctrl, & alt are pressed
    modifiers = {}
    for k in MODIFIERS.keys():
        modifiers[k] = False

    while chars:
        c = chars.pop()

        if c in list(MODIFIERS.keys()):
            keys.append((MODIFIERS[c],True))
            modifiers[c] = True

        # group of chars, for applying a modifier
        elif c == '(':
            while c != ')':
                c = _next_char(chars,'`(` without `)`')
                if c == ')':
                    raise KeySequenceError('expected a character before `)`')

                if c == ' ' and with_spaces:
                    #_handle_char(seleniumkeys['SPACE'], keys,  False)
                    keys.append(seleniumkeys['SPACE'])
                elif c == '\n' and with_newlines:
                    keys.append(seleniumkeys['ENTER'])
                    #_handle_char(seleniumkeys['ENTER'], keys, False)
                elif c == '\t' and with_tabs:
                    #_handle_char(seleniumkeys['TAB'], keys, False)
                    keys.append(seleniumkeys['TAB'])
                else:
                    #_handle_char(c,keys,False)
                    keys.append(c)
                    # if we need shift for this char and it's not already pressed
                    #shift = (c.isupper() or c in SHIFT.keys()) and not modifiers['+']
                    #if c in SHIFT.keys():
                    #    _handle_char(SHIFT[c], keys, shift)
                    #else:
                    #    _handle_char(c.lower(), keys, shift)
                c = _next_char(chars,'`)` not found')
            #_release_modifiers(keys,modifiers)

        # escaped code, modifier, or repeated char
        elif c == '{':
            saw_space = False
            name = [_next_char(chars)]
            arg = ['0']
            c = _next_char(chars, '`{` without `}`')
            while c != '}':
                if c == ' ':
                    saw_space = True
                elif c in '.0123456789' and saw_space:
                    arg.append(c)
                else:
                    name.append(c)
                c = _next_char(chars, '`{` without `}`')
            code = ''.join(name)
            arg = float('0' + ''.join(arg))
            if code == 'PAUSE':
                if not arg:
                    arg = PAUSE
                keys.append((None,arg))
            else:
                # always having 1 here makes logic
                # easier -- we can always loop
                if arg == 0:
                    arg = 1
                for i in range(int(arg)):
                    if code in list(seleniumkeys.keys()):
                        keys.append(seleniumkeys[code])
                        #_append_code(keys, seleniumkeys[code])
                    else:
                        # must be an escaped modifier or a
                        # repeated char at this point
                        if len(code) > 1:
                            raise KeySequenceError('Unknown code: %s' % code)
                        # handling both {e 3} and {+}, {%}, {^}
                        shift = code in ESCAPE and not code in NO_SHIFT
                        # do shift if we've got an upper case letter
                        shift = shift or code[0].isupper()
                        c = code
                        if not shift:
                            # handle keys in SHIFT (!, @, etc...)
                            if c in list(SHIFT.keys()):
                                c = SHIFT[c]
                                shift = True
                        _handle_char(c.lower(), keys, shift)


        # unexpected ")"
        elif c == ')':
            raise KeySequenceError('`)` should be preceeded by `(`')

        # unexpected "}"
        elif c == '}':
            raise KeySequenceError('`}` should be preceeded by `{`')

        # handling a single character
        else:
            if c in ('~','\n'):
                keys.append(seleniumkeys['ENTER'])
                #_append_code(keys, seleniumkeys['ENTER'])
            elif c == ' ':
                keys.append(seleniumkeys['SPACE'])
                #_append_code(keys, seleniumkeys['SPACE'])
            elif c == '\t':
                keys.append(seleniumkeys['TAB'])
                #_append_code(keys, seleniumkeys['TAB'])
            else:
                keys.append(c)
    return keys
