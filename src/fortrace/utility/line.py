from __future__ import absolute_import
import inspect


def lineno():
    """Returns the current line number in the program."""
    return '\n' +"_line_"+ str(inspect.currentframe().f_back.f_lineno)
