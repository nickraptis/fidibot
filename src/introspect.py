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


def parse_cmd_ispublic(name):
    return not name.endswith("_private")


def parse_cmd_isprivate(name):
    return not name.endswith("_public")


def cmd_functions_dict(context, module_name):
    """Get the command functions of a context in a list of tuples format"""
    functions = {}
    for attr in dir(context):
        cmd_name = parse_cmd_name(attr)
        if cmd_name:
            # hide commands that have the attribute hidden
            try:
                if getattr(context, attr).hidden:
                    continue
            except AttributeError:
                pass
            # add the command to available functions
            functions[attr] = {'name': cmd_name,
                               'function_name' : attr,
                               'module_name': module_name}
    return functions


# Commands to build the index #
###############################

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
