import sys
import parse
import interpreter
sys.path.append('../.') # add parent folder to  PYTHONPATH

try:
  
  f = open ("MAS3.txt","r")  # open file
  program = f.read()          # read file into data
  f.close()                   # Close the file
  print program               # print the the program
 
  tree = parse.parse(program)
  print '=================================================================================='
  print "Parse tree:"
  print tree
  print ""
  interpreter.interpret(tree)
except:
  import traceback
  traceback.print_exc()

raw_input("Press Enter key to terminate")

