# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""Determine contexts for coverage.py"""


def combine_context_switchers(context_switchers):
    """Create a single context switcher from multiple switchers.

    `context_switchers` is a list of functions that take a frame as an
    argument and return a string to use as the new context label.

    Returns a function that composites `context_switchers` functions, or None
    if `context_switchers` is an empty list.

    When invoked, the combined switcher calls `context_switchers` one-by-one
    until a string is returned.  The combined switcher returns None if all
    `context_switchers` return None.
    """
    if not context_switchers:
        return None

    if len(context_switchers) == 1:
        return context_switchers[0]

    def should_start_context(frame):
        """The combiner for multiple context switchers."""
        for switcher in context_switchers:
            new_context = switcher(frame)
            if new_context is not None:
                return new_context
        return None

    return should_start_context


def should_start_context_test_function(frame):
    """Is this frame calling a test_* function?"""
    if frame.f_code.co_name.startswith("test"):
        return qualname_from_frame(frame)
    return None


def qualname_from_frame(frame):
    """Get a qualified name for the code running in `frame`."""
    co = frame.f_code
    fname = co.co_name
    if not co.co_varnames:
        return fname

    first_arg = co.co_varnames[0]
    if co.co_argcount and first_arg == "self":
        self = frame.f_locals["self"]
    else:
        return fname

    method = getattr(self, fname, None)
    if method is None:
        return fname

    func = getattr(method, '__func__', None)
    if func is None:
        return fname

    if hasattr(func, '__qualname__'):
        qname = func.__qualname__
    else:
        for cls in getattr(self.__class__, '__mro__', ()):
            f = cls.__dict__.get(fname, None)
            if f is None:
                continue
            if f is func:
                qname = cls.__name__ + "." + fname
                break
        else:
            qname = fname
    return qname
