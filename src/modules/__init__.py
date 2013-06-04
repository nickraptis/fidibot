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


def activate_modules():
    """Return the list of active module classes, and all their string alternatives"""
    active_modules = []
    active_alternatives = {}
    for module_name in active:
        try:
            # this corresponds to `from module_name import module`
            m = __import__(module_name, globals(), locals(), [], -1)
            active_modules.append(m.module)
            active_alternatives.update(m.alternatives_dict)
        except ImportError:
            import logging
            logging.error("There isn't a module named %s to import" % module_name)
        except AttributeError as e:
            import logging
            if 'alternatives' in e.message:
                logging.debug("The module named %s doesn't provide string alternatives" % module_name)
            else:
                logging.error("The module named %s hasn't got a valid module attribute" % module_name)
    return active_modules, active_alternatives
