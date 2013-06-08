# Author: Nick Raptis <airscorp@gmail.com>
"""Collection of introspection functions for the bot"""

import inspect

# General introspection functions #
###################################

def get_full_help(doc_lines):
    """Join the doctype to produce full help string."""
    full = []
    for line in doc_lines:
        full.append(line)
    return "\n".join(full)


def get_summary(doc_lines):
    """Get the first lines of the docstrings as a summary."""
    summary = []
    for line in doc_lines:
        if line:
            summary.append(line)
        else:
            break
    return " ".join(summary)


def help_object(obj, name=None, full=False):
    """
    Get help for an object.
    
    If name is not given, it will use the function name.
    Set full=True to get full help, otherwise a summary.
    """
    if not name:
        name = obj.__name__.split('.')[-1]
    doc = inspect.getdoc(obj)
    # if the docstring is just whitespace it doesn't get cleaned
    doc = doc.strip()
    if not doc:
        return "No help found"
    doc_lines = doc.split('\n')
    if full:
        full_help = get_full_help(doc_lines)
        return " - %s:\n%s" % (name, full_help)
    else:
        summary = get_summary(doc_lines)
        return "%-10s: %s" % (name, summary)


def help_attr(obj, attr, name=None, full=False):
    """
    Get help for an object's attribute.
    
    If name is not given, it will use the function name.
    Set full=True to get full help, otherwise a summary.
    """
    return help_object(getattr(obj, attr), name=name, full=full)



# Commands relative to the bot #
################################

def parse_cmd_name(name):
    """Parse a command name from the function name."""
    if not name.startswith("cmd_"):
        return
    else:
        name = name.replace("cmd_", "")
        name = name.replace("_public", "")
        name = name.replace("_private", "")
        return name


def parse_cmd_type(name):
    """Parse public, private, or both from the function name"""
    if not (name.endswith("_private") or name.endswith("_public")):
        return 'both'
    else:
        return name.split('_')[-1]


def cmd_functions_list(context):
    """Get the command functions of a context in a list of tuples format"""
    commands = {}
    for attr in dir(context):
        cmd_name = parse_cmd_name(attr)
        cmd_type = parse_cmd_type(attr)
        if cmd_name:
            commands[attr] = (cmd_name, cmd_type)
    return commands.items()


def public_private_from_list(cmd_list):
    """Get dictionaries for private and private commands from a list"""
    public = {}
    private = {}
    # the lambda just gets the cmd_type as the comparison key
    # Since cmd_type is a string we'll get the list sorted as
    # both, private, public
    # True means that we then reverse the list
    cmd_list.sort(None, lambda x: x[1][1], True)
    for fname, (cmd_name, cmd_type) in cmd_list:
        if cmd_type == 'public':
            public[fname] = cmd_name
        elif cmd_type == 'private':
            private[fname] = cmd_name
        else:
            public[fname] = cmd_name
            private[fname] = cmd_name
    return public, private


def public_private_of_module(module):
    """Get dictionaries for private and private commands of a module"""
    context = module.context_class
    cmd_list = cmd_functions_list(context)
    return public_private_from_list(cmd_list)


def list_commands(module):
    """Get dict of available commands of a module"""
    public, private = public_private_of_module(module)
    public = public.values()
    private = private.values()
    return {'public': public, 'private': private}


if __name__ == '__main__':
    import modules.basiccmds as a
    from pprint import pprint

    methodList = [method for method in dir(a) if callable(getattr(a, method))]
    
    print help_object(a)
    print help_object(a, full=True)
    print
    
    c = a.module.context_class
    cmd_list = cmd_functions_list(c)
    print cmd_list
    print
    
    public, private = public_private_from_list(cmd_list)
    pprint(public)
    pprint(private)
    print
    
    public, private = public_private_of_module(a.module)
    pprint(public)
    pprint(private)
    print
    
    print list_commands(a.module)
    
    print 'Public:'
    for cmd in public:
        print help_attr(c, cmd, name=public[cmd])
    print
    print 'Public Full:'
    for cmd in public:
        print help_attr(c, cmd, name=public[cmd], full=True)
    print
    print 'Private:'
    for cmd in private:
        print help_attr(c, cmd, name=private[cmd])
    print
    print 'Private Full:'
    for cmd in private:
        print help_attr(c, cmd, name=private[cmd], full=True)
