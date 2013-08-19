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
active = ["ignore", "basiccmds", "update", "help", "fail", "weather", "urlparser", "dnd"]


def activate_modules():
    """Return the list of active module classes,
    and all their string alternatives"""
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
            fmt_str = "There isn't a module named %s to import"
            logging.error(fmt_str % module_name)
        except AttributeError as e:
            import logging
            if 'alternatives' in e.message:
                fmt_str = "The module named %s doesn't provide string alternatives"
                logging.debug(fmt_str % module_name)
            else:
                fmt_str = "The module named %s hasn't got a valid module attribute"
                logging.error(fmt_str % module_name)
    return active_modules, active_alternatives
