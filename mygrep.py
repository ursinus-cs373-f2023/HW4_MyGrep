def eval_nfa(s, q, delta, F, verbose=False):
    """
    Evaluate a standard NFA with no lambda arrows
     
    Parameters
    ----------
    s: string
        Input to try
    q: string
        Start state
    delta: (string, string) -> set([string])
        Transition function
    F: set([string])
        Accept states
    verbose: bool
        If True, print info about sequence of states that are visited
    """
    states = set([q]) ## We now track multiple possibilities
    if verbose:
        print("Start", states)
    for c in s:
        next_states = set([])
        for p in states:
            if (p, c) in delta:
                ## This line is different from DFA; there are multiple
                ## states we can branch out to; track the unique ones
                next_states = next_states.union(delta[(p, c)])
        states = next_states
        if verbose:
            print(c, states)
    ## At least one state must be in the set of accept states F
    return len(states.intersection(F)) > 0


def get_reachable_lambdas(start, delta):
    """
    Parameters
    ----------
    start: string
        State at which to start.  We'll gather anything
        that can be reached by a sequence of lambdas
        from this state
    delta: (string, string) -> set([string])
        Transition function
     
    Returns
    -------
    set([string])
        Set of all states reachable from start 
        by a sequence of lambda arrows
    """
    reachable = set([])
    stack = [start]
    while len(stack) > 0:
        state = stack.pop()
        reachable.add(state)
        if (state, None) in delta:
            # If there are lambda arrows out of this state, 
            # loop through all of them
            for neighbor in delta[(state, None)]:
                if not neighbor in reachable:
                    # If we haven't seen this state yet 
                    # (Crucial to avoid infinite loops for lambda cycles)
                    stack.append(neighbor)
    reachable.remove(start) # Exclude the start state itself
    return reachable


def reduce_nfa_lambdas(delta, F):
    """
    Eliminate the lambdas in an NFA by doing a reduction
    to equivalent arrows and accept states to without 
    lambdas
     
    Parameters
    ----------
    delta: (string, string) -> set([string])
        Transition function, which will be updated as as side effect
    F: set([string])
        Final states, which will be updated as as side effect
    """
    ## Step 1: Copy the dictionary into a new format where
    ## it's more convenient to look up only the arrows coming
    ## out of a particular state
    delta_state = {} #(State):(Character:set(states))
    for (state, c), states_to in delta.items():
        if not state in delta_state:
            delta_state[state] = {}
        if not c in delta_state[state]:
            delta_state[state][c] = set([])
        delta_state[state][c].update(states_to)

    ## Step 2: Loop through each state, get the new arrows, and 
    ## update the final states
    states = set([key[0] for key in delta])
    F_new = set([])
    for state in states:
        # Get states that are reachable from this state
        reachable = get_reachable_lambdas(state, delta)
        # Figure out if this should be an accept state based
        # on what's reachable
        if len(reachable.intersection(F)) > 0:
            F_new.add(state)
        # Add the new arrows
        for other in reachable:
            if other in delta_state: # If there are actually any arrows coming out of this state
                for c, states_to in delta_state[other].items():
                    if c is not None:
                        # Add this new equivalent arrow
                        if not (state, c) in delta:
                            delta[(state, c)] = set([])
                        delta[(state, c)] = delta[(state, c)].union(states_to)
    F.update(F_new)
     
    ## Step 3: Remove the original lambda arrows
    to_remove = [key for key in delta.keys() if key[1] is None]
    for key in to_remove:
        del delta[key]


def infix2postfix(expr):
    """
    Convert an infix specification of a regular expression into
    a postfix version.
    If two adjacent characters do not include ()*|, 
    then insert a . (concatenate) in between them
    Also insert a . (concatenate) after every *

    Parameters
    ----------
    expr: string
        Regular expression in infix form
    
    Returns
    -------
    An array of the postfix expression, which includes ()*|. for operators,
    and which includes "c_i" for the operands, where c is the character
    and i is the index

    Precedence: star > concatenation > union
    """
    ## Step 1: Convert infix string into infix list, escaping characters, 
    ## converting to c_i, and inserting concatenation . where necessary
    i = 0
    idx = 0
    infix = []
    while i < len(expr):
        if expr[i] in "*|()":
            infix.append(expr[i])
            if expr[i] == "*" and i < len(expr)-1:
                infix.append(".")
        else:
            if expr[i] == "\\": # Escape character
                i += 1
            c = expr[i]
            infix.append("{}_{}".format(c, idx))
            idx += 1
            if i < len(expr)-1 and expr[i+1] not in "*|)":
                infix.append(".")
        i += 1
    
    ## Step 2: Convert infix list to postfix list
    precedence = {"*":2, ".":1, "|":0}
    postfix = []
    stack = []
    for x in infix:
        if x in precedence.keys():
            while len(stack) > 0 and stack[-1] != "(" and precedence[x] <= precedence[stack[-1]]:
                postfix.append(stack.pop())
            stack.append(x)
        elif x == "(":
            stack.append(x)
        elif x == ")":
            while len(stack) > 0 and stack[-1] != "(":
                postfix.append(stack.pop())
            stack.pop()
        else:
            # Ordinary operand
            postfix.append(x)
    
    ## Step 3: Pop the rest of the operators from the stack
    while len(stack) > 0:
        postfix.append(stack.pop())
    return postfix


def eval_regexp(R, s):
    """
    Check to see if a string s is part of a regular expression R
    by converting R into an NFA and checking to see if that NFA accepts s
    This is an efficient algorithm that takes O(len(R)len(s)) time
    in the worst case

    Parameters
    ----------
    R: string
        Regular expression
    s: string
        String we're checking
    """
    pass
    ## TODO: Fill this in
