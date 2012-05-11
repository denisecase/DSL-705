#
# Modified by Denise Case for Little Language Project 4/27/12
#
# PLY template of parser for little goal language
# reads list of tokens and creates output trees as nested lists
#
# I have included some syntactic sugar to accomodate
# my hypothetical users.
# For example, "has" can be used for "possesses"
# and "triggers" can be abbreviated with ">".
#
# I included "at time T" to make it more descriptive,
# so domain experts can read the language easily,
# but power users can type "at T" during development.
#
"""LANGUAGE SYNTAX ****************************************************
--------------------------------------------------
CL : CommandList            C  : Command 
IL : VariableList           I  : Variable
F  : Fact                   N  : Numeral
E  : Expression             K  : Comment
AL : AchievesList          AB : AchievesBlock
PL : PossessesList         PB : PossessesBlock
--------------------------------------------------
         
CL ::= sequence of zero or more C,  separated by semicolons
IL ::= sequence of zero or more I,  separated by commas

C ::=       > IL at /?time?/ T    // trigger goal(s) at time t
    | trigger IL at /?time?/ T    // trigger goal(s) at time t
    | delete  IL at /?time?/ T    // delete  goal(s) at time t
    |  F                          // enter a fact in the knowledgebase
    | I1 assigned I2 to I3 at /?time?/ T   // agent assigned role to goal at time t

E ::= I or  E2                     // disjunctive child goals expression
    | I and E2    |   I & E2       // conjunctive child goals expression
    | I
    
F ::=  I = E                       // assigns child goals E to goal I
    | I (NUM1, NUM2)               // assigns data values 1 and 2 to goal I
    | I (NUM1, NUM2, NUM3, NUM4)   // assigns data values 1, 2, 3, 4 to goal I
    | I1 > IL   | I1 triggers IL   // goal1 triggers goal(s)
    | I  requires IL               // role1 requires capability(s)
    | I  achieves AL               // role1 achieves goal [to 88%], goal2, goal3 [to 75%]
    | I  possesses PL              // agent  possesses capability1 [at 77%], cap2, etc
    | I  has       PL              // agent  possesses capability1 [at 77%], cap2, etc

AL ::=  sequence of zero or more AB,  separated by commas   // achieves list
AB  ::= I /?to NUM?/                                        // achieves block

PL ::=  sequence of zero or more PB,  separated by commas   // possesses list
PB  ::= I /?at NUM?/                                        // possesses block

N ::=  string of digits
I ::=  string of chars, not including keywords
K ::=   /    /?...?/                                       // comment

and /?...?/  means that ... is optional

OUTPUT TREES AS NESTED LISTS ******************************************

CLIST ::=  [ CTREE* ]  a list of zero or more  CTREEs
ILIST ::=  [ I* ]      a list of zero or more  Is
DLIST ::=  [ DTREE* ]  a list of zero or more  DTREEs  

CTREE ::=  ["trigger",ILIST,T]   |  ["delete", ILIST,T]  | F
         | ["assigned",I1,I2,I3,NUM] // NUM can be 'nil'
         
ETREE ::=  ["and", I, ETREE] | ["or", I, ETREE]  | I

FTREE ::=  ["parentgoaldef", I, ETREE ]
        |  ["leafgoaldef",  I, NLIST]
        |  ["triggerdef", I, ILIST]
        |  ["requires", I, DLIST]
        |  ["achieves", I, DLIST]  
        |  ["possesses",I, DLIST]

DTREE ::= [I, NUM] | I   // and identifier and the optional degree (e.g. 77%)
        
********************************************************************"""

from ply import *
import lex 

tokens = lex.tokens  # get tokens - individual units of language

######################################################

# Grammar rules and their corresponding operator trees:

### THE FIRST GRAMMAR RULE DEFINES THE START (MAIN) NONTERMINAL:

# CL ::= C;*  (that is,   CL ::=  C | C ; CL | empty )
# CLIST ::= [ CTREE+ ]
def p_CommandList(p):
    '''CommandList : Command
                   | Command ';' CommandList
                   | empty '''
    if len(p) == 2 and p[1] != None :  # CommandList : Command
       p[0] = [p[1]]
    elif len(p) == 4 :  # CommandList :  Command ';' CommandList
       p[0] = [p[1]] + p[3]
    else :  # CommandList : empty,  because p[1] == None
       p[0] = []


# just being flexible - some may like it descriptive, some concise :)
# C ::=   > I at /?time?/ T  |  trigger I at /?time?/ T     
#   | delete  I at /?time?/ T    
#   |  F
#   | ["assigned",I1,I2,I3,NUM] // NUM can be 'nil'
# CTREE ::=  ["trigger",I,T]   |  ["delete", I,T]   | F
def p_Command1(c):
    '''Command : '>' ID at time NUM'''
    c[0] = ["trigger", c[2], c[5]]

def p_Command2(c):
    '''Command : '>' ID at NUM'''
    c[0] = ["trigger", c[2], c[4]]
    
def p_Command3(c):
    '''Command : trigger IdentifierList at time NUM'''
    c[0] = ["trigger", c[2], c[5]]

def p_Command4(c):
    '''Command : trigger IdentifierList at NUM'''
    c[0] = ["trigger", c[2], c[4]]
    
def p_Command5(c):
    '''Command : delete IdentifierList at time NUM'''
    c[0] = ["delete", c[2], c[5]]

def p_Command6(c):
    '''Command : delete IdentifierList at NUM'''
    c[0] = ["delete", c[2], c[4]]

def p_Command7(c):
    '''Command : Fact '''
    c[0] = c[1]

def p_Command8(c):
    '''Command : ID assigned ID to ID at NUM  '''
    c[0] = ["assigned", c[1], c[3], c[5], c[7]]
    
def p_Command9(c):
    '''Command : ID assigned ID to ID at time NUM  '''
    c[0] = ["assigned", c[1], c[3], c[5], c[8]]



# IL ::= I,*  (that is,   IL ::=  I ITAIL | empty   
#                         ITAIL ::=  , I ITAIL  |  empty    )
# ILIST ::= [ I* ]
def p_IdentifierList1(t):
    '''IdentifierList : ID IListTail'''
    t[0] = [t[1]] + t[2]

def p_IdentifierList2(t):
    '''IdentifierList :  empty'''
    t[0] = []

def p_IListTail1(t):
    '''IListTail : ',' ID IListTail'''
    t[0] = [t[2]] + t[3]

def p_IListTail2(t):
    '''IListTail : empty'''
    t[0] = []



# F ::=  I = E  | I (NL)   | I1 > I2  
# FTREE ::= ["parentgoaldef", I,ETREE ] | ["leafgoaldef", I, NLIST] | ["triggerdef", I1, I2]
# |  ["requires", I, BLIST] |  ["achieves", I, BLIST] |  ["possesses",I, BLIST]
# |  ["treedef", I, ELIST]
def p_Fact1(e):
    '''Fact : ID '=' Expression '''
    e[0] = ["parentgoaldef", e[1], e[3]]

def p_Fact2(e):
    ''' Fact : ID '(' NUM ',' NUM ')' '''
    e[0] = ["leafgoaldef", e[1], e[3], e[5]]
    
def p_Fact3(e):
    ''' Fact : ID '(' NUM ',' NUM ',' NUM ',' NUM ')' '''
    e[0] = ["leafgoaldef", e[1], e[3], e[5], e[7], e[9]]
   
def p_Fact4(e):
    ''' Fact : ID '>' ID '''
    e[0] = ["triggerdef", e[1], e[3]]

def p_Fact5(e):
    ''' Fact : ID triggers ID '''
    e[0] = ["triggerdef", e[1], e[3]]
    
def p_Fact6(e):
    ''' Fact : ID requires DegreeList '''   
    e[0] = ["requires", e[1], e[3]]

def p_Fact7(e):
    ''' Fact :  ID achieves DegreeList '''   
    e[0] = ["achieves", e[1], e[3]]

def p_Fact8(e):
    ''' Fact : ID possesses DegreeList '''   
    e[0] = ["possesses", e[1], e[3]]

def p_Fact9(e):
    ''' Fact : ID has DegreeList '''   
    e[0] = ["possesses", e[1], e[3]]



# DL ::= D;*  (that is,   DL ::=  D | D , DL | empty )
# DLIST ::= [ DTREE+ ]
def p_DegreeList(d):
    '''DegreeList : DegreeBlock
                   | DegreeBlock ',' DegreeList
                   | empty '''
    if len(d) == 2 and d[1] != None :  # DegreeList : DegreeBlock
       d[0] = [d[1]]
    elif len(d) == 4 :  # DegreeList :  DegreeBlock ';' DegreeList
       d[0] = [d[1]] + d[3]
    else :  # DegreeList : empty,  because p[1] == None
       d[0] = []


# D ::= I at NUM   | I to E  | I
# DTREE ::=  [I, NUM] | I
def p_DegreeBlock1(d):
    '''DegreeBlock : ID at NUM '''
    d[0] = [d[1], d[3]]
    
def p_DegreeBlock2(d):
    '''DegreeBlock : ID to NUM '''
    d[0] = [d[1], d[3]]

def p_DegreeBlock3(d):
    '''DegreeBlock : ID  '''
    d[0] = [d[1]]


# E ::= I or E   | I and E |  I & E2   | I
# ETREE ::=  ["and", I, E] | ["or", I, E]  | I
def p_SubExpression1(e):
    '''Expression : ID or Expression '''
    e[0] = ["or", e[1], e[3]]
    
def p_SubExpression2(e):
    '''Expression : ID and Expression '''
    e[0] = ["and", e[1], e[3]]

def p_SubExpression3(e):
    '''Expression : ID  '''
    e[0] = e[1]
    
def p_SubExpression6(e):
    '''Expression : ID '&' Expression '''
    e[0] = ["and", e[1], e[3]]






#### Generic empty construction --- no token at all
def p_empty(p):
    '''empty : '''
    pass   # retains  p[0] = None


#### Parse Error handler : prints location of error and quits parser
def p_error(p):
    print "SYNTAX ERROR at LexToken(grammar_phrase, input_word, line_number, char_number):"
    print (15 * " "), p
    print "PARSER QUITS."
    raise Exception

bparser = yacc.yacc()

def parse(data,debug=0):
    bparser.error = 0
    p = bparser.parse(data,debug=debug)
    if bparser.error: return None
    return p

