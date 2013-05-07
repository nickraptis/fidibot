# Author: Nick Raptis <airscorp@gmail.com>
"""
Modules package for fidibot.

Interesting attributes
----------------------
active: A list of module names to import. Add modules here to activate them.

active_modules: The list of active module classes.
                This what you'd probably want to import.

Base classes
------------
Base classes live in the 'basemodule' file.
"""

# define modules to get functionality from
active = ["basiccmds", ]

# this line is a programmatical way to do
# from module_name import module
# for each item in our 'active' list
# you shouldn't need to mess with it.
active_modules = [__import__(m, globals(), locals(), [], -1).module for m in active]