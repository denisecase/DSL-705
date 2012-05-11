#
# Modified by Denise Case for Little Language Project 4/27/12
#
# Interpreter for little goal language.

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


E ::= I or  E2   |   I | E2             // disjunctive child goals expression
    | I and E2   |   I + E2 |   I & E2  // conjunctive child goals expression
    | I
    
F ::=  I = E                       // assigns child goals E to goal I
    | I (NUM1, NUM2)               // assigns data values 1 and 2 to goal I
    | I (NUM1, NUM2, NUM3, NUM4)   // assigns data values 1,2,3 and 4 to goal I
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
K ::= /   /?...?/                    // allows user comments that will be ignored

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
 
### The interpretation functions:

def interpretCLIST(clist) : # no return value (runs command list)
    """param: clist  is a tree of form  CLIST ::=  [ CTREE* ]
    """
    for command in clist :
        interpretCTREE(command)


def interpretCTREE(c) :   # runs a command
    """param: c  is a command represented as a CTREE:
       CTREE ::=   ["trigger",  I, NUM ] |  ["delete", I, NUL ]  |  FTREE
    """
    operator = c[0]
    if operator in ('leafgoaldef', 'parentgoaldef', 'triggerdef','achieves','requires','possesses') : # facts
        interpretFTREE(c)              # interpret the associated fact tree
    elif operator == ">" or operator == "trigger" :
        for g in c[1] :
            print 'EVENT: ',g, ' triggered at time ',c[2]
            events[int(c[2])]=g
    elif operator == "delete" :
        print 'EVENT: ',c[1], ' deleted at time ',c[2]
        events[c[2]]= '-'+c[1]
    elif operator == "assigned" :
        print 'EVENT: ','agent ', c[1], ' assigned role ',c[2], ' to get',c[3],' at time ',c[4]
        loadDictionary(agentAssignedDict, c[1], c[2],1)  # dict : agent -> role
        loadDictionary(roleAssignedDict, c[2], c[3],1)   # dict : role  -> goal
    else :   # error
        crash("invalid command", c)


def interpretFTREE(f) : # interprets facts
    """ param: ftree  is a tree of form
        FTREE ::=  ["parentgoaldef", I,ETREE ]  |  ["leafgoaldef", I,NUM, NUM]  |  ["triggerdef", I1, I2]
    """
    goal = f[1] 
    if  f[0] == "leafgoaldef" :
         print "FACT:  ", goal, " will persist for ~", f[2], " time units before resolving at ",f[3],"% success rate."
         if len(f) == 4 :
             data = (f[2],f[3])  # time, success % forced
         if len(f) > 4 :
            data = (f[2],f[3],f[4],f[5])  # scheduled
         goals[goal] = ('nil',data) # no children,  leaf goal data
         triggers[goal] = []  # set downstream list to empty
    elif f[0] == "parentgoaldef" :
         print "FACT:  ", goal, "is parent goal of ", f[2] # ["and/or",g2,g3]
         kidlist = []
         kidlist.append(f[2][1])
         kidlist.append(f[2][2])
         if f[2][0] == 'and' :
             kidclosure = ('and',kidlist)  # list of conjunctive child goals
         else :
             kidclosure = ('or',kidlist)  # list of disjunctive child goals
         goals[goal] = (kidclosure,'nil') # kid closure, not a leaf therefore no leaf goal data
    elif f[0] == "triggerdef" :
         if triggers == {} :  # if triggers dict is empty
             downstreamlist = []
         else :
             downstreamlist = triggers[goal]  # get initial set of down stream triggered goals
         for g in f[2] :
              downstreamlist.append(g)  # add this goal to its downstream list
         triggers[goal] = downstreamlist
    elif f[0] == "requires" :
        print "FACT:  ", f[1], " requires ", f[2]
        loadDictionary(requiresDict, f[1], f[2],0)  # dict : role -> list capabilities
    elif f[0] == "achieves" :
         print "FACT:  ", f[1], " achieves ", f[2]
         loadDictionary(achievesDict, f[1], f[2],0) # dict : role -> goals
    elif f[0] == "possesses" :
         print "FACT:  ", f[1], " possesses ", f[2]
         loadDictionary(capsDict, f[1], f[2],0)  # dict : agent -> list of capabilities

### additional supporting functions

def loadDictionary(dict, key, newList,isOneToOne) :
    if dict == {} : # if requiresDict is empty;  dict : role -> list capabilities
        lst = []
    else :
        if key in dict :
            lst = dict[key]  # get list of capabilties defined thus far
        else :
            lst = []
    if isOneToOne == 1 :
        lst.append(newList)
    else : 
        for item in newList :
            lst.append(item)  # add this capability to list required for role 
    dict[key] = lst   

def printTime(t) :
    """  Given a time, t, print the status of all the goal lists
         params: simulation time t as an integer 
    """
    print t,'\tACTIVE=',actList,'\tR=', remList,'\tACH=',achList,'\tF=',failList,'\tO',obvList

def printRealTimeHeader(topName) :
    """  Print heading for real time data section uses the name of the top goal.
    """
    h = 'DateTime\t\t'
    for s in sensorDict :
        h = h +s + '\t '
    h = h + 'All\t'
    for s in sensorDict :
        h = h +'G\t '
    h = h + 'TOP GOAL'
    print '-------------------------------------------------------------------------------------------------' 
    print h
    print '-------------------------------------------------------------------------------------------------' 
    
def printTimeSet(t, lstData, overallData, lstSucc, okAll, overallReliability) :
    """  Print data for real time data section
    """
    h = t +'\t'
    for d in lstData :
        h = h + d + '\t\t'
    h = h + overallData + '\t'
    for s in lstSucc :
        h = h + s + '\t'
    h = h + okAll + '\t' + "%.2f" % overallReliability + "%"
    print h

def topgoal() :   # returns id of top goal
    """  Gets the overall goal - at the top of the goal tree (has no parents)
         returns: the indentifier of the top goal 
    """
    print len(goals)
    possible = goals.copy()
    for g in goals :                # look through the set of all goals
        print ' building goal tree ', g  # left in for display purposes
        kidclosure = goals[g][0]    # get the closure describing the children of each active goal
        if kidclosure != 'nil' :    # if there are children
            for goal in kidclosure[1] :
                if goal[0] == 'and' or goal[0] == 'or' :
                    possible.pop(goal[1])
                    print ' top goal cannot be ', goal[1]
                    possible.pop(goal[2])
                    print ' top goal cannot be ', goal[2]
                else:
                    possible.pop(goal)
                    print ' top goal cannot be ', goal
    return possible.keys()  # the one remaining will be the root goal

def calcReliability(g) :   # returns reliability of a goal
    """  Given a  goal calculate the reliability from goal tree. 
         param:  goal identifier 
    """
    kidclosure = goals[g][0]    # get the closure describing the children of each active goal
    data = goals[g][1]          # get the closure describing the data
    if kidclosure == 'nil' and len(data) == 2 :    # if leaf goal with 2 params failure
        mttr = float(data[0])
        mtbf = float(data[1])
        rel = 1. - mttr/(mtbf+mttr)
        print ' rel of ', g , ' = ', rel, '(mtbf = ', mtbf, ' mttr =  ', mttr, ')'
        return rel  # the calculated reliability
    if kidclosure == 'nil' and len(data) == 4 :    # if leaf goal with 4 params maint
        cycYrs = float(data[0])
        stDay = float(data[1])
        outHrs = float(data[2])
        firstYr =float(data[3])
        rel = 1. - outHrs/(cycYrs*8760.)
        print ' rel of ', g , ' = ', rel, '(cycYrs = ', cycYrs, ' stDay =  ', stDay, ' outHrs = ', outHrs, ' firstYr =  ', firstYr,')'
        return rel  # the calculated reliability
    type = kidclosure[0]
    kidlist = kidclosure[1]
    if type == 'and':  # handle conjuntively joined goals
         prod = 1
         for sib in kidlist :
            if sib[0] == 'and' :
                   prod = prod * calcReliability(sib[1]) * calcReliability(sib[2])
            else :
                   prod = prod * calcReliability(sib)
         print ' rel of ', g , ' = ',  prod
         return prod
    if type == 'or':   # handle disjunctively joined goals
         assert len(kidlist) == 2;
         r1 = calcReliability(kidlist[0])
         r2 = calcReliability(kidlist[1])
         rel = r1 + r2 - r1*r2
         print ' rel of ', g , ' = ', rel
         return rel
         
def propagateSuccess(goal) :
    """  Given a goal that was successfully achieved,
         propagate the impacts on any active parent goals. 
         param: successfully achieved goal identifier
    """
    for g in actList :              # look through the set of all active goals
        kidclosure = goals[g][0]    # get the closure describing the children of each active goal
        if kidclosure != 'nil' :    # if there are children
            type = kidclosure[0]
            kidlist = kidclosure[1]
            if type == 'or':  # and this goal has a disjunctive parent, achieve parent and obviate siblings
                if goal in kidlist :
                    achieve(g)             # achieve parent
                    for sib in kidlist :
                        if sib != goal and sib in actList :
                            obviate(sib)   # obviate siblings
                    propagateSuccess(g)
            else :
                if goal in kidlist :  # if this goal has a conjunctive parent, if all its siblings are acheived than parent is too.
                    countUnachieved = 0
                    for sib in kidlist :
                        if sib not in achList :
                            countUnachieved = countUnachieved + 1
                    if countUnachieved == 0 :
                        achieve(g)
                        propagateSuccess(g)

def propagateFailure(goal) :
    """  Given a goal that was not successfully achieved,
         propagate the impacts on any active parent goals. 
         param: failed goal identifier
    """
    for g in goals :
        kidclosure = goals[g][0]   # get the closure describing the children of each goal
        if kidclosure != 'nil' :
            type = kidclosure[0]
            kidlist = kidclosure[1]
            if type == 'and':  # if this goal has a conjunctive parent, fail parent also 
                if goal in kidlist :
                    fail(g)
                    propagateFailure(g)
            else :              # if this goal has a disjunctive parent, see if this was the last hope
                if goal in kidlist : 
                    countActiveSibs = 0
                    for sib in kidlist :
                        if sib in actList :
                            countActiveSibs = countActiveSibs + 1
                    if countActiveSibs == 0 :
                        fail(g)
                        propagateFailure(g)
                
def achieve(goal) :
    """  Given a goal that was successfully achieved,
         remove it from the ACTIVE list and add it to the ACHIEVED list 
         param: successfully achieved goal identifier
    """
    if not (goal in achList) :
        achList.append(goal)

def obviate(goal) :
    """  Given a goal that was deemed obviated i.e. unnecessary due to a disjunctive sibling being achieved,
         remove it from the ACTIVE list and add it to the OBVIATED list 
         param: obviated goal identifier
    """
    actList.remove(goal)
    if not (goal in obvList) :
        obvList.append(goal)

def fail(goal) :
    """  Given a goal that failed,
         remove it from the ACTIVE list and add it to the FAILED list 
         param: failed goal identifier
    """
    if not (goal in failList) :
        failList.append(goal)             

def activateChildGoals(goal,t) :
    """  Given a goal triggered at time t
         schedule the time when the goal will be resolved and 
         activate any child goals 
         params: triggered goal identifier, time (int) the goal was triggered
    """
    print 'activate child goal ', goal, ' at time ', t
    if goal not in goals :   # there is a goal missing either leaf data or child goals
        msg = 'Missing inputs - '+goal+' needs either leaf data or child goals'
        crash(msg, goal)
    kidclosure = goals[goal][0]  # get the closure with this goal's children
    if kidclosure == 'nil' :     # ('and',f[2][1]), (time, pctsuccess) for children & leaf goal data
        return                   # no children - return
    for childgoal in kidclosure[1] :       # for every child goal
        if childgoal[0] == 'and' or childgoal[0] == 'or' :
            actList.append(childgoal[1])          # add it to the active list
            activateChildGoals(childgoal[1],t)    # and recursively activate the child's children
            actList.append(childgoal[2])          # add it to the active list
            activateChildGoals(childgoal[2],t)    # and recursively activate the child's children

        else :
            actList.append(childgoal)          # add it to the active list
            activateChildGoals(childgoal,t)    # and recursively activate the child's children

def updateResolveTime(goal,t) :
    """  Given a goal triggered at time t
         schedule the time when the goal will be resolved and 
         activate any child goals 
         params: triggered goal identifier, time (int) the goal was triggered
    """
    data = goals[goal][1]  # (duration before goal is likely to be resolved, percent likelihood of success)
    if data != 'nil' :
        dur = data[0]            # duration before goal is likely to be resolved
        pctSuccess = data[1]     # percent likelihood of success
        schedTime = t + int(dur)  # resolve time is approximately the current time + the delay
        futureTime = int(random.uniform(int(schedTime * .9), int(schedTime*1.3)))
        entry = (goal,pctSuccess)    # create an entry for the resolve times dict
        if futureTime in resolveTimes :
            list = resolveTimes[futureTime]   # if that time already has an entry, get the existing list
        else :
            list = []                         # if no entry, initialize an empty list
        list.append(entry)                    # append this entry to this resolve time's list
        resolveTimes[futureTime] = list       # update the resolve times dictionary

def startSensors() :
    """  Start up any sensors defined. These specical capabilities must
         have a name that starts with Sensor.
    """
    for agent in capsDict :
        lstCaps = capsDict[agent]
        for cap in lstCaps :
            capname = cap[0]
            if capname.startswith('Sensor') :
                startSensor(capname)

def startSensor(sensor) :
    """  Start up a simulated real time data sensor
         by opening the file for reading and adding to a dict of sensor data
    """
    datalist = []
    try:
        filename = "data/"+ sensor + ".csv"
        f = open (filename,"r")  # open file
        dialect = csv.Sniffer().sniff(f.read(1024))
        f.seek(0)
        reader = csv.reader(f, dialect)
        datalist.extend(reader)
        sensorDict[sensor] = datalist   
        f.close()
       
    except:
       print "error starting sensor data - check for data/fn.csv file where fn is same as sensor capability"

def getGoalParams(sensor) :
    goal = getGoal(sensor)
    return goals[goal][1]

def getGoal(sensor) :
    # find agent from sensor capability  agent -> lst capabilities
    agent = (key for key,value in capsDict.items() if value[0][0] == sensor ).next()
    # find role assigned to agent
    role = agentAssignedDict[agent][0]
    # find goal this role was assigned to
    goal = roleAssignedDict[role][0]
    return goal

###########################

def crash(message, tree) :
    """prints an error message and stops the interpreter
       params: message - a string to print
               tree - the parse tree that caused the error
    """
    print "CRASH: " + message
    print "At phrase:", tree
    print
    raise Exception   # stops the interpreter

def crashg(message) :  # generic crash ; no tree
    """prints an error message and stops the interpreter
       params: message - a string to print
               tree - the parse tree that caused the error
    """
    print "CRASH: " + message 
    print
    raise Exception   # stops the interpreter

# MAIN FUNCTION ###########################################################
import random
import csv

def interpret(tree) :
    """interprets a complete program tree
       param: tree is a program tree, namely, a  CLIST 
    """
    # initialize the data structures:
    global  events, triggers, goals, resolveTimes, actList, remList, achList, failList, obvList, \
            capsDict, sensorDict, agentAssignedDict, roleAssignedDict, achievesDict, requiresDict
    events = {}      # dict of timed events t -> events
    triggers = {}    # dict of triggers goal -> triggered goals
    goals = {}       # dict of goals -> child goals
    actList = []     # list of active goals
    remList = []     # list of removed goals  - not used but kept for consistency with OMACS
    achList = []     # list of achieved goals
    failList = []    # list of failed goals
    obvList = []     # list of obviated goals (made unnecessary) - not used but kept for consistency with OMACS
    capsDict = {}    # dict : agent -> list of capabilities 
    sensorDict = {}  # dict : sensor -> sensor data
    agentAssignedDict = {}# dict : agent -> role
    roleAssignedDict = {} # dict : role -> goal
    achievesDict = {}     # dict : role -> goal
    requiresDict = {}     # dict : role -> list capabilities
  
    print ''
    print '=================================================================================='
    print 'Interpreting Model '
    print '=================================================================================='
    interpretCLIST(tree)  #interpret the program commands
    print ''
    print '=================================================================================='
    print 'Starting Reliability Calculations '
    print '=================================================================================='
    print ''
    top = topgoal();
    print top
    if len(top) <> 1 :
        crashg(' Configuration error: only 1 top goal allowed, but specified more. Check for data values.')
    topName = top[0]
    print '\nSearching through tree.  Top goal is:  ',topName, '\n'
    if capsDict == {} :
        rel = calcReliability(topName)*100
        print ''   
        print '=================================================================================='
        print 'Overall Reliability for ', topName, ' is ', rel,'%'
        print '=================================================================================='
        print ''
    else :
        print '========================================================================================================'
        print 'Starting Timed Results '
        print '========================================================================================================' 
        tmax = 100
        countOK = 0
        startSensors()  # start up any real-time measurement devices
        for t in range (1, tmax+1) :
            if t in events :  # first process events that occur at this time
                goal = events[t]
                print ''
                if goal not in obvList :
                    actList.append(goal) # add this goal to the active list
                    activateChildGoals(goal,t)  # if it has child goals, activate them too.
                    # if any required capabilities are sensors, start the sensor monitor
                    # goal -> role -> agent -> capability
                printRealTimeHeader(topName)  # print a data section header
            first = 1
            dataList = []
            achievesList = []
            sum = 0.0
            sumMax = 0.0
            for s in sensorDict :
                dataset = sensorDict[s]
                row = list(dataset)[t+1]
                if first :
                    dateVal = row[0]
                    first = 0
                val = float(row[1])
                data = getGoalParams(s)
                goal = getGoal(s)
                goalName = goals[goal][0]
                max = float(data[1])/100.0 # first is min, second data item is max
                if val <= max :
                    achievesList.append('ok')
                    countOK = countOK + 1.0
                    achieve(goal)
                    propagateSuccess(goal)
                else :
                    achievesList.append('-')
                    fail(goal)
                    propagateFailure(goal)
                sum = sum +val
                sumMax = sumMax + max
                dataList.append("%.4f" % float(val))
            if sum <= sumMax :
                achievesAll = 'OK'
                countOK = countOK + 1.0
            else :
                achivesAll = '-'
            pctOK = countOK/t*100.0/float(len(sensorDict) + 1)
            printTimeSet(dateVal, dataList,"%.2f" % sum,achievesList,achievesAll, pctOK)   
        print ''
        print '========================================================================================================'
        if topName not in failList :
            print 'SYSTEM IS CONTINUOUSLY SUCCESSFUL'
        else :
            print 'TOP GOAL HAS AT LEAST PARTIALLY FAILED '
            print '========================================================================================================'
            print 'Failures include: ',failList
        print '========================================================================================================'
        print ''
# end