#
# Modified by Denise Case for Little Goal Language  4/27/12
#
# PLY template of scanner (lexical analyzer) for little goal language
# reads strings and creates a list of tokens, one for each language unit

from ply import *

# Define keywords:
keywords = ('or','and','at','time','delete', 'trigger', 'triggers',
            'achieves','to','requires','possesses','has','assigned')

# Define token names used in parse rules:
primitives = ('ID', 'NUM')  
tokens = keywords + primitives 

# Define literal symbols used in parse rules:
literals = [';',  '=', '(', ')',  '+', '&','|', ',', '>','{','}']

# Define tokens for primitive names to be recognized by parser:

t_ignore = ' \t\r'

def t_ID(t):   # defines an  ID  token or a keyword
    r'[A-Za-z][a-zA-Z0-9]*'
    if t.value in keywords:  # is token  t  a keyword?
        t.type = t.value
    return t
    
t_NUM = r'\d+'   # defines a NUM token

def t_NEWLINE(t):
    r'\n'
    t.lexer.lineno += 1
    #return t

def t_COMMENT(t):
     r'\/.*'
     pass
    #return - doesn't return anything; ignores comments

# Error token:
def t_error(t):
    print("Illegal character %s" % t.value[0])
    t.lexer.skip(1)

# initialize the lexical analyzer:
lexer = lex.lex(debug=0)



