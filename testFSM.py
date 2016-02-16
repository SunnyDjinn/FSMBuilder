
from FSM import *

print "Creating x as follows..."
x = FSM(1, [])
x.addTransition(1, 2, 'a')
x.addTransition(1, 3, 'b')
x.addTransition(2, 3, 'b')
x.grantAcceptingState(3)
print x.toString()

k = FSM.kleene(x)

print k.toString()
#k.draw()

dfsm = FSM.determinise(k)
print dfsm.toString()
#dfsm.draw()



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

