
import copy
from graphviz import Digraph

SPECIAL_STATE_CHARACTER = '$$'
EPSILON = '###'

# Class Transition
# Defines a transition with a from state, a to state and a symbol
class Transition:
	def __init__(self, fromState, toState, symbol):
		self.fromState = fromState
		self.toState = toState
		self.symbol = symbol

	def toString(self):
		return str(self.fromState) + ", " + str(self.toState) + ", " + str(self.symbol)

# Class Finite State Machine
# Defines a FSM with an initial state, a set of accepting states and a matrix of its transitions
class FSM:

	def __init__(self, initialState, acceptingStates):
		try:
			self.initialState = initialState
			self.acceptingStates = set()
			self.states = set()
			for state in acceptingStates:
				self.acceptingStates.add(state)
			for state in acceptingStates:
				self.states.add(state)

			self.states.add(initialState)
			self.transitions = set()
		except TypeError:
			print "Usage: FSM((int)<initialState>, (set, list) <acceptingStates>)"
			return None

	def addTransition(self, fromState, toState, symbol):
		self.transitions.add(Transition(fromState, toState, symbol))
		self.states.add(fromState)
		self.states.add(toState)

	def removeTransition(self, fromState, toState, symbol):
		for transition in self.transitions:
			if transition.fromState == fromState and transition.toState == toState and transition.symbol == symbol:
				self.transitions.remove(transition)
				break

	def removeLonelyStates(self):
		for state in self.states:
			if self.initialState != state and not existsTransitionFrom(state) and not existsTranstitionTo(state):
				self.states.remove(state)
				self.acceptingStates.remove(state)

	def existsTransitionFrom(self, fromState):
		for transition in self.transitions:
			if transition.fromState == fromState:
				return True
		return False

	def existsTranstitionTo(self, toState):
		for transition in self.transitions:
			if transition.toState == toState:
				return True
		return False

	def addState(self, state):
		self.states.add(state)

	def removeState(self, state):
		if state == self.initialState:
			self.initialState = None
		transitionsToRemove = set()
		for transition in self.transitions:
			if state == transition.fromState:
				transitionsToRemove.add(transition)
			elif state == transition.toState:
				transitionsToRemove.add(transition)
		for transition in transitionsToRemove:
			self.transitions.remove(transition)
		self.states.remove(state)
		if state in self.acceptingStates:
			self.acceptingStates.remove(state)

	def replaceInitialState(self, newInitialState):
		self.initialState = newInitialState

	def createElem(self, fromState, toState, symbol):
		self.addTransition(Transition(fromState, toState, symbol))

	def grantAcceptingState(self, state):
		if state not in self.acceptingStates and state in self.states:
			self.acceptingStates.add(state)

	def ungrantAcceptingState(self, state):
		if state in self.acceptingStates:
			self.acceptingStates.remove(state)

	def toString(self):
		return ("Initial State: " + str(self.initialState) + '\n' 
				+ '\n'.join(transition.toString() for transition in sorted(self.transitions, key=lambda x: x.fromState))
				+ '\nAccepting States: ' + ", ".join(str(state) for state in sorted(self.acceptingStates)) + '\n')

	def renameState(self, state, newState):
		if newState in self.states:
			print "Cannot rename: state " + str(state) + " already existing"
			return None
		if newState == SPECIAL_STATE_CHARACTER:
			print "State Name Reserved"
			return None
		transitionsToAdd = set()
		willGrantAcceptingState = False
		willGrantInitialState = False
		if state in self.acceptingStates:
			willGrantAcceptingState = True
		if(self.initialState == state):
			willGrantInitialState = True
		for transition in self.transitions:
			if state == transition.fromState and state == transition.toState:
				transitionsToAdd.add((newState, newState, transition.symbol))
			elif state == transition.fromState:
				transitionsToAdd.add((newState, transition.toState, transition.symbol))
			elif state == transition.toState:
				transitionsToAdd.add((transition.fromState, newState, transition.symbol))
		self.removeState(state)
		self.addState(newState)
		if willGrantInitialState:
			self.replaceInitialState(newState)
		if willGrantAcceptingState:
			self.grantAcceptingState(newState)
		for transition in transitionsToAdd:
			self.addTransition(transition[0], transition[1], transition[2])

	def renameStates(self, specialStateCharacter, stateCounter):
		statesToRename = copy.deepcopy(sorted(self.states, reverse=True))
		
		while len(statesToRename) > 0:
			state = statesToRename.pop()
			self.renameState(state, specialStateCharacter + str(stateCounter))
			stateCounter += 1
		return stateCounter


	# Draws the FSM using the dot language and graphviz
	def draw(self):
		g = Digraph(filename='./temp/tmp.gv', format='png')
		g.body.extend(['rankdir=LR'])

		# accepting states
		g.attr('node', shape='doublecircle')
		for state in self.acceptingStates:
			g.node(str(state))

		# other states
		g.attr('node', shape='circle')
		for state in self.states:
			if not state in self.acceptingStates:
				g.node(str(state))

		# transitions
		for transition in self.transitions:
			g.edge(str(transition.fromState), str(transition.toState), str(transition.symbol))

		# Initial state initialization
		g.attr('node', shape='plaintext')
		g.node('')
		g.edge('', str(self.initialState))

		g.view()




	@staticmethod 
	def union(fsm1, fsm2):
		copyFsm1 = copy.deepcopy(fsm1)
		copyFsm2 = copy.deepcopy(fsm2)
 
		stateCounter = copyFsm1.renameStates(SPECIAL_STATE_CHARACTER, 1)
		stateCounter = copyFsm2.renameStates(SPECIAL_STATE_CHARACTER, stateCounter)

		unitedFSM = FSM(0, copyFsm1.states | copyFsm2.states)
		unitedFSM.acceptingStates = copyFsm1.acceptingStates | copyFsm2.acceptingStates
		unitedFSM.addTransition(0, copyFsm1.initialState, EPSILON)
		unitedFSM.addTransition(0, copyFsm2.initialState, EPSILON)
		for transition in copyFsm1.transitions:
			unitedFSM.addTransition(transition.fromState, transition.toState, transition.symbol)
		for transition in copyFsm2.transitions:
			unitedFSM.addTransition(transition.fromState, transition.toState, transition.symbol)

		unitedFSM.renameStates('', 0)

		return unitedFSM

	@staticmethod 
	def concat(fsm1, fsm2):
		copyFsm1 = copy.deepcopy(fsm1)
		copyFsm2 = copy.deepcopy(fsm2)
 
		stateCounter = copyFsm1.renameStates(SPECIAL_STATE_CHARACTER, 0)
		stateCounter = copyFsm2.renameStates(SPECIAL_STATE_CHARACTER, stateCounter)

		concatFSM = FSM(copyFsm1.initialState, copyFsm1.states | copyFsm2.states)
		for state in copyFsm1.acceptingStates:
			concatFSM.addTransition(state, copyFsm2.initialState, EPSILON)

		concatFSM.acceptingStates = copyFsm2.acceptingStates

		for transition in copyFsm1.transitions:
			concatFSM.addTransition(transition.fromState, transition.toState, transition.symbol)
		for transition in copyFsm2.transitions:
			concatFSM.addTransition(transition.fromState, transition.toState, transition.symbol)

		concatFSM.renameStates('', 0)

		return concatFSM

	@staticmethod
	def kleene(fsm):
		kleenedFsm = copy.deepcopy(fsm)
		kleenedFsm.renameStates(SPECIAL_STATE_CHARACTER, 1)
		
		for state in kleenedFsm.acceptingStates:
			kleenedFsm.addTransition(state, kleenedFsm.initialState, EPSILON)

		kleenedFsm.addState(0)
		kleenedFsm.addTransition(0, kleenedFsm.initialState, EPSILON)
		kleenedFsm.replaceInitialState(0)
		kleenedFsm.grantAcceptingState(kleenedFsm.initialState)

		kleenedFsm.renameStates('', 0)

		return kleenedFsm

	def __epsilonAccessible(self, state):
		epsilonAccessible = set()
		epsilonAccessible.add(state)
		for transition in self.transitions:
			if transition.fromState == state and transition.symbol == EPSILON:
				epsilonAccessible.add(transition.toState)

		untreatedStates = list(epsilonAccessible)
		while len(untreatedStates) > 0:
			currentState = untreatedStates.pop(0)
			for transition in self.transitions:
				if currentState not in epsilonAccessible and transition.fromState == currentState and transition.symbol == EPSILON:
					epsilonAccessible.add(currentState)
					untreatedStates.append(currentState)

		return epsilonAccessible
	
	def __computeAlphabet(self):
		alphabet = set(transition.symbol for transition in self.transitions)
		if EPSILON in alphabet:
			alphabet.remove(EPSILON)
		return alphabet

	@staticmethod
	def determinise(fsm):
		fsm.renameStates(SPECIAL_STATE_CHARACTER, 0)
		epsStates = {str(state):fsm.__epsilonAccessible(state) for state in fsm.states}
		alphabet = fsm.__computeAlphabet()

		newTransitions = []
		activeStates = []
		activeStates.append(epsStates[str(fsm.initialState)])
		activeStatesPointer = 0

		while(activeStatesPointer < len(activeStates)):
			for symbol in alphabet:
				newState = set()
				for q in activeStates[activeStatesPointer]:
					for transition in fsm.transitions:
						if transition.fromState == q and transition.symbol == symbol:
							for state in epsStates[str(transition.toState)]:
								newState.add(state)
				
				if setToString(newState) != None:
					newTransitions.append((setToString(activeStates[activeStatesPointer]), setToString(newState), symbol)) 				
				if setToString(newState) != None and newState not in activeStates:
					activeStates.append(newState)
				del newState
			activeStatesPointer += 1

		DFSM = FSM(setToString(activeStates[0]), [])
		
		for transition in newTransitions:
			DFSM.addTransition(transition[0], transition[1], transition[2])

		for newState in activeStates:
			for exState in newState:
				if exState in fsm.acceptingStates:
					DFSM.grantAcceptingState(setToString(newState))

		DFSM.renameStates('', 0)
		return DFSM


	def match(self, string):
		currentState = self.initialState;
		currentStringIndex = 0

		# All transitions from the current state
		transitionsFromCurrentState = set(transition for transition in self.transitions if transition.fromState == currentState)
		
		# all transitions that matches something at the right index of the string
		matchingSet = set(transition for transition in transitionsFromCurrentState if string.find(transition.symbol) == currentStringIndex)
		
		for transition in matchingSet:
			print transition.toString()




def setToString(stateSet):
	if len(stateSet) == 0:
		return None
	stringSet = ""
	for item in stateSet:
		stringSet += str(item)
	return stringSet
		
