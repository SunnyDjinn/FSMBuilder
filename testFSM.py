
from FSM import *

print "Creating x as follows..."
x = FSM(1, [])
x.addTransition(1, 2, 'ab')
x.addTransition(1, 3, 'b')
x.addTransition(2, 3, 'b')
x.grantAcceptingState(3)
#print x.toString()

x.breakMultipleCharactersTransitions()

print x.toString()

k = FSM.kleene(x)

k.addTransition(1, 3, 'bb')
k.removeTransition(1, 3, 'b')
print k.toString()


print "Determinising..."
dfsm = FSM.determinise(k)
print dfsm.toString()
dfsm.draw()

print "Is abbbbbbabb in dfsm? : " + str(dfsm.match("abbbbbbabb")) 	# True
print "Is abb in dfsm? : " + str(dfsm.match("abb"))		# True
print "Is bb in dfsm? : " + str(dfsm.match("bb"))		# True
print "Is a in dfsm? : " + str(dfsm.match("a"))			# False
print "Is b in dfsm? : " + str(dfsm.match("b"))			# False
print "Is aa in dfsm? : " + str(dfsm.match("aa"))			# False
print "Is bb in dfsm? : " + str(dfsm.match("bb"))		# True
print "Is c in dfsm? : " + str(dfsm.match("c"))			# True

exit()
