# Author: Nick Raptis <airscorp@gmail.com>
"""
Modules package for fidibot.

Interesting attributes
----------------------
active: A list of module names to import. Add modules here to activate them.

Base classes
------------
Base classes live in the 'basemodule' file.
"""

# define modules to get functionality from
active = ["ignore", "basiccmds", "urlparser"]


def active_modules():
    """Return the list of active module classes."""
    active_modules = []
    for module_name in active:
        try:
            # this corresponds to `from module_name import module`
            active_modules.append(__import__(module_name, globals(), locals(), [], -1).module)
        except ImportError:
            import logging
            logging.error("There isn't a module named %s to import" % module_name)
        except AttributeError:
            import logging
            logging.error("The module named %s hasn't got a valid module attribute" % module_name)
    return active_modules
