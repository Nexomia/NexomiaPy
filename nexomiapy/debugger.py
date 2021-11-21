from inspect import getframeinfo, stack
def p(*args):
  caller = getframeinfo(stack()[1][0])
  print("Failed :(\nTraceback => \n\tIn file %s on line %d - " % (caller.filename, caller.lineno), *args) 