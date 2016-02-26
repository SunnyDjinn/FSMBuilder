
import copy
from graphviz import Digraph

SPECIAL_STATE_CHARACTER = '$$'
EPSILON = '###'

class Transition:
	""" 
	Class Transition
 	Defines a transition with a from state, a to state and a symbol
	"""
	def __init__(self, fromState, toState, symbol):
		self.fromState = str(fromState)
		self.toState = str(toState)
		self.symbol = str(symbol)

	def toString(self):
		return str(self.fromState) + ", " + str(self.toState) + ", " + str(self.symbol)


class FSM:
	"""
	Class Finite State Machine
	Defines a FSM with an initial state, a set of accepting states and a matrix of its transitions
	"""
	def __init__(self, initialState, acceptingStates):
		"""
			FSM Constructor
			Takes an initial state and an iterable object of accepting states
		"""
		try:
			self.initialState = str(initialState)
			self.acceptingStates = set()
			self.states = set()
			for state in acceptingStates:
				self.acceptingStates.add(str(state))
			for state in acceptingStates:
				self.states.add(str(state))

			self.states.add(str(initialState))
			self.transitions = set()
		except TypeError:
			print "Usage: FSM((int)<initialState>, (set, list) <acceptingStates>)"
			return None

	def addTransition(self, fromState, toState, symbol):
		"""
		Adds a transition to the FSM
		Takes a beginning state, and arrival state, and a symbol to define the transition
		"""
		fromState = str(fromState)
		toState = str(toState)
		symbol = str(symbol)
		if symbol == "":
			print "Cannot add transition: symbol field empty"
			return
		self.transitions.add(Transition(fromState, toState, symbol))
		self.states.add(fromState)
		self.states.add(toState)

	def removeTransition(self, fromState, toState, symbol):
		"""
		Removes a transition from the FSM
		Idintifies the transition with the beginning state, the arrival state and its associated symbol
		"""
		fromState = str(fromState)
		toState = str(toState)
		symbol = str(symbol)
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
		fromState = str(fromState)
		for transition in self.transitions:
			if transition.fromState == fromState:
				return True
		return False

	def existsTranstitionTo(self, toState):
		toState = str(toState)
		for transition in self.transitions:
			if transition.toState == toState:
				return True
		return False

	def isTransitionIn(self, fromState, toState, symbol):
		fromState = str(fromState)
		toState = str(toState)
		symbol = str(symbol)
		for transition in self.transitions:
			if(transition.fromState == fromState and transition.toState == toState and transition.symbol == symbol):
				return True
		return False

	def __whereToTransition(self, fromState, symbol):
		"""
			Determines where does a transition from fromState goes to, when reading symbol. /!\ HAS TO BE DETERMINISTIC /!\
		"""
		fromState = str(fromState)
		symbol = str(symbol)
		if not self.existsTransitionFrom(fromState):
			return None
		for transition in self.transitions:
			if transition.fromState == fromState and transition.symbol == symbol: 
				return transition.toState					# assuming only one exist, which should be the case if deterministic

	def addState(self, state):
		self.states.add(str(state))

	def removeState(self, state):
		state = str(state)
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
		self.initialState = str(newInitialState)

	def createElem(self, fromState, toState, symbol):
		self.addTransition(Transition(fromState, toState, symbol))

	def grantAcceptingState(self, state):
		state = str(state)
		if state not in self.acceptingStates and state in self.states:
			self.acceptingStates.add(state)

	def ungrantAcceptingState(self, state):
		state = str(state)
		if state in self.acceptingStates:
			self.acceptingStates.remove(state)

	def toString(self):
		return ("Initial State: " + str(self.initialState) + '\n' 
				+ '\n'.join(transition.toString() for transition in sorted(self.transitions, key=lambda x: x.fromState))
				+ '\nAccepting States: ' + ", ".join(str(state) for state in sorted(self.acceptingStates)) + '\n')

	def renameState(self, state, newState):
		state = str(state)
		newState = str(newState)
		if newState in self.states:
			print "Cannot rename: state " + str(newState) + " already existing"
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
			state = str(statesToRename.pop())
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

		newInitialState = SPECIAL_STATE_CHARACTER + str(0)
		kleenedFsm.addState(newInitialState)
		kleenedFsm.addTransition(newInitialState, kleenedFsm.initialState, EPSILON)
		kleenedFsm.replaceInitialState(newInitialState)
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

	def hasSymbolTransition(self, fromState, symbol):
		for transition in self.transitions:
			if transition.fromState == fromState and transition.symbol == symbol:
				return True
		return False

	def addDeadState(self, deadState):
		""" 
		Adds a dead state to a FSM when it is deterministic but not complete. For every state and every symbole, if there does not 
		exist a transition from the  state with the symbol, it adds such a transition to a dead state, where nothing is reachable from 
		"""
		deadState = str(deadState)
		alphabet = self.__computeAlphabet()
		transitionsToAdd = set()

		for symbol in alphabet:
			for fromState in self.states:
				if not self.hasSymbolTransition(fromState, symbol):
					transitionsToAdd.add(Transition(fromState, deadState, symbol))
		for transition in transitionsToAdd:
			self.addTransition(transition.fromState, transition.toState, transition.symbol)
		# adding transitions from dead state to itself
		for symbol in alphabet:
			self.addTransition(deadState, deadState, symbol)

	def breakMultipleCharactersTransitions(self):
		""" For every single transition that requires multiple characters at the same time, breaks the transition into multiple ones, 
		adding required new states """
		stateCounter = self.renameStates(SPECIAL_STATE_CHARACTER, 0)
		transitions = copy.deepcopy(self.transitions)

		for transition in transitions:
			if transition.symbol == EPSILON:
				continue
			if len(str(transition.symbol)) > 1:
				self.removeTransition(transition.fromState, transition.toState, transition.symbol)
				self.addTransition(transition.fromState, SPECIAL_STATE_CHARACTER + str(stateCounter), str(transition.symbol)[0] ) # first transition
				stateCounter += 1
				for character in range(2, len(str(transition.symbol))-1): # intermediate transitions
					self.addTransition(SPECIAL_STATE_CHARACTER + str(stateCounter-1), SPECIAL_STATE_CHARACTER + str(stateCounter), str(transition.symbol)[character])
					stateCounter += 1
				self.addTransition( SPECIAL_STATE_CHARACTER + str(stateCounter-1), transition.toState, str(transition.symbol)[len(str(transition.symbol))-1]) # last transition

		self.renameStates('', 0)

#
#
# Refactor determinise
#
#
	@staticmethod
	def determinise(fsmUnmodified):
		""" Determinises a NDFSM into and FSM - removes epsilon transitions, multiple chracters symbols and multiple transitions for the
		same character between equivalent pairs of states """
		fsm = copy.deepcopy(fsmUnmodified)
		fsm.breakMultipleCharactersTransitions()

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

		lastStateIndex = DFSM.renameStates('', 0)
		DFSM.addDeadState(lastStateIndex)

		return DFSM


	@staticmethod
	def minimize(fsmUnmodified):
		fsm = FSM.determinize(fsmUnmodified)
		alphabet = fsm.__computeAlphabet()
		classes = set()
		classes.add(set(fsm.acceptingStates), set(state for state in fsm.states if state not in fsm.acceptingStates))
		changesMade = True
		while changesMade:
			changesMade = False
			newClasses = set()
			for eqClass in classes:
				if len(eqClass) > 1:
					eqClassStatesTransTable = {}
					for state in eqClass:
						stateGoesTo = []
						# look at each state and build a table?
						for c in alphabet:
							stateGoesTo.append(eqClass for eqClass in classes if fsm.__whereToTransition(state, c) in eqClass)
							# how to remember which state goes where when decided?
						eqClassStatesTransTable[state] = stateGoesTo
						del stateGoesTo
					#for key in eqClassStatesTransTable:

						# I don't know where I'm going right now. Needs to be thought before trying anything. Will tryi again later



	def match(self, string):
		""" Tries to match an input string to the FSM. If, at the end of the input string, 
		the current state is accepting, returns True, else returns false """

		fsm = FSM.determinise(self)

		alphabet = fsm.__computeAlphabet()
		currentState = fsm.initialState;
		currentStringIndex = 0

		while currentStringIndex != len(string):
			
			if string[currentStringIndex] not in alphabet:
				return False

			currentState = fsm.__whereToTransition(currentState, string[currentStringIndex])
			currentStringIndex += 1

		if currentState in fsm.acceptingStates:
			return True
		return False




def setToString(stateSet):
	""" Returns the string related to the name of a set of states (concatenation of names of those sets) """
	if len(stateSet) == 0:
		return None
	stringSet = ""
	for item in stateSet:
		stringSet += str(item)
	return stringSet
		
