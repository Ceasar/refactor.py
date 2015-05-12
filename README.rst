
refactor.py
===========

**refactor.py** is a script to help Python programmers automatically refactor modules,
specifically aimed at fixing problems that tend to occur in the real-world.

refactor.py has the following features:
  
- Rewrite ``from a import *`` statements to only import what's necessary.

- Extract definitions (i.e. classes, functions, constants, etc) from one module to another (possibly new) module,
  removing unneeded imports and filling in necessary imports as appropriate. This allows you to decompose monolithic modules
  or combine trivial modules to quickly try out different configurations.

- Suggest different ways to break apart monolithic modules into smaller ones to increase coherency.

- Make nested functions flat.

- Eliminate redundant boolean statements.

  For example. ``refactor.py`` will transform::
  
    def foo():
      if a:
        return False
      if b:
        return False
      if c:
        return True
      return False
      
  Into::
  
    def foo():
      return -a and -b or c
