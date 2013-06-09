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

def get_name(obj):
    """Get unqualified name."""
    return obj.__name__.split('.')[-1]

def help_object(obj, name=None, full=False):
    """
    Get help for an object.
    
    If name is not given, it will use the function name.
    Set full=True to get full help, otherwise a summary.
    """
    if not name:
        name = get_name(obj)
    doc = inspect.getdoc(obj)
    if not doc:
        return "No help found"
    # if the docstring is just whitespace it doesn't get cleaned
    doc = doc.strip()
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

def parse_cmd_ispublic(name):
    return not name.endswith("_private")

def parse_cmd_isprivate(name):
    return not name.endswith("_public")

def cmd_functions_list(context):
    """Get the command functions of a context in a list of tuples format"""
    commands = {}
    for attr in dir(context):
        cmd_name = parse_cmd_name(attr)
        cmd_type = parse_cmd_type(attr)
        if cmd_name:
            commands[attr] = (cmd_name, cmd_type)
    return commands.items()

def cmd_functions_dict(context, module_name):
    """Get the command functions of a context in a list of tuples format"""
    functions = {}
    for attr in dir(context):
        cmd_name = parse_cmd_name(attr)
        if cmd_name:
            functions[attr] = {'name': cmd_name,
                               'function_name' : attr,
                               'module_name': module_name}
    return functions

def public_private_from_list(fnc_list):
    """
    Get dictionaries for private and private commands
    from a functions list
    """
    public = {}
    private = {}
    # the lambda just gets the cmd_type as the comparison key
    # Since cmd_type is a string we'll get the list sorted as
    # both, private, public
    # True means that we then reverse the list
    fnc_list.sort(None, lambda x: x[1][1], True)
    for fname, (cmd_name, cmd_type) in fnc_list:
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
    fnc_list = cmd_functions_list(context)
    return public_private_from_list(fnc_list)


def list_commands(module):
    """Get dict of available commands of a module"""
    public, private = public_private_of_module(module)
    public = public.values()
    private = private.values()
    return {'public': public, 'private': private}


########################################################################

def build_module_index(module):
    mod_file = inspect.getmodule(module)
    mod_name = get_name(mod_file)
    
    mod_index = {'summary': help_object(mod_file, mod_name),
                   'help': help_object(mod_file, mod_name, True)}
    
    context = module.context_class
    mod_index['functions'] = cmd_functions_dict(context, mod_name)
    functions = mod_index['functions']
    
    for fname in functions:
        cmd_name = functions[fname]['name']
        f = getattr(context, fname)
        functions[fname].update({'summary': help_object(f, cmd_name),
                                'help': help_object(f, cmd_name, True)})
    public = {}
    for fname in functions:
        cmd_name = functions[fname]['name']
        if parse_cmd_ispublic(fname):
            public[cmd_name] = functions[fname]
    mod_index['public'] = public
    
    private = {}
    for fname in functions:
        cmd_name = functions[fname]['name']
        if parse_cmd_isprivate(fname):
            private[cmd_name] = functions[fname]
    mod_index['private'] = private
    
    return mod_name, mod_index


def build_index(modules):
    index = {'modules': {}}

    public = {}
    private = {}
    
    mods = index['modules']
    for module in modules:
        mod_name, mod_index = build_module_index(module)
        mods[mod_name] = mod_index
        public.update(mod_index['public'])
        private.update(mod_index['private'])

    index.update({'public': public, 'private': private})
    return index


if __name__ == '__main__':
    from pprint import pprint as pp
    from modules import activate_modules
    modules, alts = activate_modules()

    index = build_index(modules)
    pp(index)
