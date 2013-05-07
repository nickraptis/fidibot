active = ["basiccmds", ]

active_modules = [__import__(m, globals(), locals(), [], -1).module for m in active]