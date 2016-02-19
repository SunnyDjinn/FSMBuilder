
from FSM import *

print "Creating x as follows..."
x = FSM(1, [])
x.addTransition(1, 2, 'ab')
x.addTransition(1, 3, 'b')
x.addTransition(2, 3, 'b')
x.grantAcceptingState(3)
print x.toString()

x.breakMultipleCharactersTransitions()

print x.toString()
x.draw()

exit()
k = FSM.kleene(x)

print k.toString()
#k.draw()

dfsm = FSM.determinise(x)
print dfsm.toString()
dfsm.draw()

exit()

print "Creating y as follows..."
y = FSM(4, [])
y.addTransition(4, 5, 'c')
y.addTransition(5, 6, 'd')
y.addTransition(5, 6, 'c')
y.grantAcceptingState(6)
y.grantAcceptingState(4)
print y.toString()

print "Uniting x and y..."
z = FSM.union(x, y)
print z.toString()

#z.draw()

print "w = Concatenating x and y..."
w = FSM.concat(x, y)
print w.toString()

#w.draw()


deter = FSM.determinise(w)
print "Determizing w"
print deter.toString()
deter.draw()

print deter.match("a");
print deter.match("b");
print deter.match("aa");
print deter.match("abcc");

